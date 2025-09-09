##### requirements #####
import pandas as pd # type: ignore
import numpy as np
from datetime import datetime, timezone
import matplotlib.pyplot as plt  # type: ignore
from matplotlib.backends.backend_pdf import PdfPages # type: ignore
from matplotlib.ticker import MultipleLocator
from mpl_toolkits.mplot3d import Axes3D # type: ignore
import seaborn as sns # type: ignore
from scipy.interpolate import RegularGridInterpolator # type: ignore
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster # type: ignore
from sklearn.linear_model import LinearRegression # type: ignore
from sklearn.preprocessing import StandardScaler # type: ignore
from sklearn.cluster import AgglomerativeClustering # type: ignore
from sklearn.manifold import TSNE # type: ignore
from ast import literal_eval
import sys
import matplotlib.colors as mcolors
from .Variables import el_nino_years, la_nina_years
from tqdm.notebook import tqdm




# optional 1) !pip install koreanize-matplotlib 2) import koreanize_matplotlib 3) %matplotlib inline

pd.set_option('mode.chained_assignment',  None) 

### Data filtering ###
def select_location(num_threshold, phenology_data):             # num_threshold = min # of observation
    column_names = ['bud_burst_date', 'flowering_date']
    for column_name in column_names:
        phenology_data[column_name] = pd.to_datetime(phenology_data[column_name], errors='coerce')
    
    location_list = []
    for location, group_df in phenology_data.groupby('location'):
        if group_df['flowering_date'].dt.year.count() >= num_threshold:
            location_list.append(location)
    
    return location_list


def select_data(location_list, phenology_data, temperature_data):          # filter the data with location_list
    phenology_data = phenology_data[phenology_data['location'].isin(location_list)]
    temperature_data['tm'] = pd.to_datetime(temperature_data['tm'])
    temperature_data = temperature_data[temperature_data['location'].isin(location_list)]
    
    return phenology_data, temperature_data


### Bud-burst. Flowering Prediction based on Chill-Days Model Formulas ###
class ChillDayFormula():
    def calculate_chilldays(row, Tc):   # Tc = temperature_threshold
        Tn = row['minTa']
        Tx = row['maxTa']
        Tm = row['avgTa']

        if 0 <= Tc <= Tn <= Tx:
            return 0
        elif 0 <= Tn <= Tc < Tx:
            return round(-((Tm - Tn) - (((Tx - Tc)**2) / (2 * (Tx - Tn)))), 7)
        elif 0 <= Tn <= Tx <= Tc:
            return round(-(Tm - Tn), 7)
        elif Tn < 0 <= Tx <= Tc:
            return round(-((Tx / (Tx - Tn)) * (Tx / 2)), 7)
        elif Tn < 0 < Tc < Tx:
            return round(-((Tx / (Tx - Tn)) * (Tx / 2) - (((Tx - Tc)**2) / (2 * (Tx - Tn)))), 7)
        elif Tx < 0:
            return 0

    def calculate_anti_chilldays(row, Tc):
        Tn = row['minTa']
        Tx = row['maxTa']
        Tm = row['avgTa']

        if 0 <= Tc <= Tn <= Tx:
            return Tm - Tc
        elif 0 <= Tn <= Tc < Tx:
            return round(((Tx - Tc) ** 2) / (2 * (Tx - Tn)), 7)
        elif 0 <= Tn <= Tx <= Tc:
            return 0
        elif Tn < 0 <= Tx <= Tc:
            return 0
        elif Tn < 0 < Tc < Tx:
            return round(((Tx - Tc) ** 2) / (2 * (Tx - Tn)), 7)
        elif Tx < 0:
            return 0
        else:
            return 0  # Added an else condition to handle cases not covered by the if-elif blocks



class phenology_prediction():
    def budburst(yearly_temperature_data, temperature_threshold, chill_requirement, heat_requirement):
        # set the start date of calculating chill days
        start_index = 0
        for index, row in yearly_temperature_data.iterrows():
            if row['minTa'] >= temperature_threshold:
                start_index += 1
            else:
                break
        
        yearly_temperature_data = yearly_temperature_data.iloc[start_index:].reset_index(drop=True)
            
        # calculate the accumulation of chill days
        yearly_temperature_data['chilldays'] = yearly_temperature_data.apply(lambda row: ChillDayFormula.calculate_chilldays(row, temperature_threshold), axis = 1)
        yearly_temperature_data['cd_accumulation'] = yearly_temperature_data['chilldays'].cumsum()
        
        # dormancy release date
        if (yearly_temperature_data['cd_accumulation'] <= chill_requirement).any():
            dormancy_release_date = yearly_temperature_data[yearly_temperature_data['cd_accumulation'] <= chill_requirement].iloc[0]['tm']
        else:
            dormancy_release_date = None
        
        if dormancy_release_date is None:
            return None, None

        # calculate the accumulation of anti-chill days
        heat_data = yearly_temperature_data[yearly_temperature_data['tm'] > dormancy_release_date]
        heat_data['anti_chilldays'] = heat_data.apply(lambda row: ChillDayFormula.calculate_anti_chilldays(row, temperature_threshold), axis = 1)
        heat_data['anti_chilldays'] = heat_data['anti_chilldays'].apply(lambda x: x if x > 0 else 0)
        heat_data['acd_accumulation'] = heat_data['anti_chilldays'].cumsum()
        
        # find the calculated budburst date
        if (heat_data['acd_accumulation'] >= heat_requirement).any():
            budburst_date = heat_data[heat_data['acd_accumulation'] >= heat_requirement].iloc[0]['tm']
        else:
            budburst_date = None
        
        return dormancy_release_date, budburst_date


    def predict_budburst(temperature_data, phenology_data, location_list, temperature_threshold_list, chill_requirement_list, min_obs, max_obs):        #min/max_obs: range of your analysis
        phenology_data['bud_burst_date'] = pd.to_datetime(phenology_data['bud_burst_date'])
        phenology_data['year'] = phenology_data['bud_burst_date'].dt.year
        phenology_data['year'] = phenology_data['year'].fillna(0).astype(int)
        
        Tc_used = []
        Cr_used = []
        Root_Mean_Squared_Error = []
        
        for temperature_threshold in temperature_threshold_list:
            for chill_requirement in chill_requirement_list:
                results = []
                
                # Make location_temp_data and budburst prediction
                for location in location_list:
                    location_temperature_data = temperature_data[temperature_data['location'] == location]
                    for year in range(min_obs, max_obs+1):
                        start_date = datetime(year-1, 9, 1)
                        end_date = datetime(year, 6, 1)
                        yearly_temperature_data = location_temperature_data[(location_temperature_data['tm'] >= start_date) & (location_temperature_data['tm'] < end_date)]
                    
                        if not yearly_temperature_data.empty:
                            dormancy_release_date, budburst_date = phenology_prediction.budburst(yearly_temperature_data, temperature_threshold, chill_requirement, abs(chill_requirement))
                            if budburst_date is not None:
                                results.append([location, year, budburst_date])
                results_df = pd.DataFrame(results, columns= ['location', 'year', 'budburst_prediction'])
    
    
                differs = []
                for location in location_list:
                    location_observed_data = phenology_data[phenology_data['location'] == location]
                    location_estimated_data = results_df[results_df['location'] == location]
                    
                    for year in range(min_obs, max_obs):
                        if location_observed_data['bud_burst_date'].dt.year.isin([year]).any() and location_estimated_data['year'].isin([year]).any():
                            observed_date = location_observed_data[location_observed_data['bud_burst_date'].dt.year == year]['bud_burst_date'].iloc[0]
                            estimated_date = location_estimated_data[location_estimated_data['year'] == year]['budburst_prediction'].iloc[0]
                            difference = (observed_date - estimated_date).days
                                
                            if difference is not None:
                                differs.append(difference)
                        
                # calculate Root Mean Squared Error(RMSE)
                if differs:
                    rmse = np.sqrt(np.mean(np.square(differs)))
                else:
                    rmse = None
                    
                Tc_used.append(temperature_threshold)
                Cr_used.append(chill_requirement)
                Root_Mean_Squared_Error.append(rmse)

        parameterset_rmse_df = pd.DataFrame({
            'temperature_threshold': Tc_used,
            'chill_requirement': Cr_used,
            'RMSE': Root_Mean_Squared_Error
        })
        
        return parameterset_rmse_df


    def flowering(yearly_temperature_data, temperature_threshold, chill_requirement, heat_requirement, day_length, year):
        # set the start date of calculating chill days
        start_index = 0
        for index, row in yearly_temperature_data.iterrows():
            if row['minTa'] >= temperature_threshold:
                start_index += 1
            else:
                break
        
        yearly_temperature_data = yearly_temperature_data.iloc[start_index:].reset_index(drop=True)
        
        # calculate the accumulation of chill days
        yearly_temperature_data['chilldays'] = yearly_temperature_data.apply(lambda row: ChillDayFormula.calculate_chilldays(row, temperature_threshold), axis = 1)
        yearly_temperature_data['cd_accumulation'] = yearly_temperature_data['chilldays'].cumsum()
        
        # dormancy release date
        if (yearly_temperature_data['cd_accumulation'] <= chill_requirement).any():
            dormancy_release_date = yearly_temperature_data[yearly_temperature_data['cd_accumulation'] <= chill_requirement].iloc[0]['tm']
        elif (yearly_temperature_data[(yearly_temperature_data['tm'] >= f'{year}-01-31') & (yearly_temperature_data['ssDur'] >= day_length)]).any().any():
            dormancy_release_date = yearly_temperature_data[yearly_temperature_data['ssDur'] >= day_length].iloc[0]['tm']
        else:
            dormancy_release_date = None
        
        if dormancy_release_date is None:
            return None, None
        
        # calculate the accumulation of anti-chill days
        heat_data = yearly_temperature_data[yearly_temperature_data['tm'] > dormancy_release_date]
        heat_data['anti_chilldays'] = heat_data.apply(lambda row: ChillDayFormula.calculate_anti_chilldays(row, temperature_threshold), axis = 1)
        heat_data['anti_chilldays'] = heat_data['anti_chilldays'].apply(lambda x: x if x > 0 else 0)
        heat_data['acd_accumulation'] = heat_data['anti_chilldays'].cumsum()
        
        # find the calculated flowering date
        if (heat_data['acd_accumulation'] >= heat_requirement).any():
            flowering_date = heat_data[heat_data['acd_accumulation'] >= heat_requirement].iloc[0]['tm']
        else:
            flowering_date = None
        
        return dormancy_release_date, flowering_date
    
    
    def predict_flowering(temperature_data, phenology_data, location_list, temperature_threshold_list, chill_requirement_list, heat_requirement_list, day_length_list = [24], min_obs=1973, max_obs=2025):
        phenology_data['flowering_date'] = pd.to_datetime(phenology_data['flowering_date'])
        phenology_data['year'] = phenology_data['flowering_date'].dt.year
        phenology_data['year'] = phenology_data['year'].fillna(0).astype(int)
        phenology_data_sizecheck = phenology_data[(phenology_data['year'] >= min_obs) & (phenology_data['year'] <= max_obs)]['flowering_date'].notna().sum()
        
        Tc_used = []
        Cr_used = []
        Hr_used = []
        Lc_used = []
        Mean_Absolute_Error = []
        Root_Mean_Squared_Error = []
        
        for temperature_threshold in tqdm(temperature_threshold_list, desc= 'temperature_threshold', position=0, total=len(temperature_threshold_list), leave=True, mininterval=20):
            for chill_requirement in tqdm(chill_requirement_list, desc= 'chill_requirement', position=1, total=len(chill_requirement_list), leave= False, mininterval=20):
                for heat_requirement in tqdm(heat_requirement_list, desc= 'heat_requirement', position=2, total=len(heat_requirement_list), leave= False, mininterval=20):
                    for day_length in tqdm(day_length_list, desc= 'day_length', position=3, total=len(day_length_list), leave= False, mininterval=20):
                        results = []
                        
                        if abs(chill_requirement) > heat_requirement:
                            continue
                        
                        if day_length == 24:
                            tqdm.write(f"PhenoFECT is current traveling past seasons with Parameters: {temperature_threshold}, {chill_requirement}, {heat_requirement}")
                        else:
                            tqdm.write(f"PhenoFECT is current traveling past seasons with Parameters: {temperature_threshold}, {chill_requirement}, {heat_requirement}, {day_length}")

                        
                        for location in location_list:
                            location_temperature_data = temperature_data[temperature_data['location'] == location]
                            for year in range(min_obs, max_obs+1):
                                start_date = datetime(year-1, 9, 1)
                                end_date = datetime(year, 6, 1)
                                yearly_temperature_data = location_temperature_data[(location_temperature_data['tm'] >= start_date) & (location_temperature_data['tm'] < end_date)]

                                if not yearly_temperature_data.empty:
                                    dormancy_release_date, flowering_date = phenology_prediction.flowering(yearly_temperature_data, temperature_threshold, chill_requirement, heat_requirement, day_length, year)
                                    if flowering_date is not None:
                                        results.append([location, year, flowering_date])
                        results_df = pd.DataFrame(results, columns = ['location', 'year', 'flowering_prediction'])
                        
                        # filtering parameter that is not appropriate for prediction
                        if results_df['flowering_prediction'].isnull().sum() > int(0.1 * phenology_data_sizecheck):
                            continue
                        
                        differs = []
                        for location in location_list:
                            location_observed_data = phenology_data[phenology_data['location'] == location]
                            location_estimated_data = results_df[results_df['location'] == location]
                            
                            for year in range(min_obs, max_obs):
                                if location_observed_data['flowering_date'].dt.year.isin([year]).any() and location_estimated_data['year'].isin([year]).any():
                                    observed_date = location_observed_data[location_observed_data['flowering_date'].dt.year == year]['flowering_date'].iloc[0]
                                    estimated_date = location_estimated_data[location_estimated_data['year'] == year]['flowering_prediction'].iloc[0]
                                    difference = (observed_date - estimated_date).days
                                    
                                    if difference < 0:
                                        difference = -difference
                                    
                                    if difference is not None:
                                        differs.append(difference)
                                        
                        if differs:
                            rmse = round(np.sqrt(np.mean(np.square(differs))), 3)
                            mae = round(np.mean(differs), 3)
                        else:
                            rmse = None
                            mae = None
                        
                        Tc_used.append(temperature_threshold)
                        Cr_used.append(chill_requirement)
                        Hr_used.append(heat_requirement)
                        Lc_used.append(day_length)
                        Mean_Absolute_Error.append(mae)
                        Root_Mean_Squared_Error.append(rmse)
            
        parameterset_error_df = pd.DataFrame({
            'temperature_threshold': Tc_used,
            'chill_requirement': Cr_used,
            'heat_requirement': Hr_used,
            'day_length': Lc_used,
            'MAE': Mean_Absolute_Error,
            'RMSE': Root_Mean_Squared_Error
        })
            
        return parameterset_error_df
    
    def bestfit(temperature_data, phenology_data, location_list, temperature_threshold, chill_requirement, heat_requirement, day_length=24, min_obs=1973, max_obs=2025, sorting = False, errortype = 'MAE'):
        phenology_data['flowering_date'] = pd.to_datetime(phenology_data['flowering_date'])
        phenology_data['year'] = phenology_data['flowering_date'].dt.year
        phenology_data['year'] = phenology_data['year'].fillna(0).astype(int)
        
        results = []
        for location in location_list:
            location_temperature_data = temperature_data[temperature_data['location'] == location]
            for year in range(min_obs, max_obs+1):
                start_date = datetime(year-1, 9, 1)
                end_date = datetime(year, 6, 1)
                yearly_temperature_data = location_temperature_data[(location_temperature_data['tm'] >= start_date) & (location_temperature_data['tm'] < end_date)]

                if not yearly_temperature_data.empty:
                    dormancy_release_date, flowering_date = phenology_prediction.flowering(yearly_temperature_data, temperature_threshold, chill_requirement, heat_requirement, day_length, year)
                    if flowering_date is not None:
                        results.append([location, year, dormancy_release_date, flowering_date])
        results_df = pd.DataFrame(results, columns = ['location', 'year', 'dormancy_release_date', 'flowering_prediction'])            
        if day_length == 24:
            results_df.to_csv(f'ChillDayModel_bestfit, Tc_{temperature_threshold}, Cr_{chill_requirement}, Hr_{heat_requirement}.csv', index = False)
        else: 
            results_df.to_csv(f'ChillDayModel_bestfit, Tc_{temperature_threshold}, Cr_{chill_requirement}, Hr_{heat_requirement}, Lc_{day_length}.csv', index = False)
        
        differs = []
        for location in location_list:
            location_observed_data = phenology_data[phenology_data['location'] == location]
            location_estimated_data = results_df[results_df['location'] == location]
            
            for year in range(min_obs, max_obs+1):
                if location_observed_data['flowering_date'].dt.year.isin([year]).any() and location_estimated_data['year'].isin([year]).any():
                    observed_date = location_observed_data[location_observed_data['flowering_date'].dt.year == year]['flowering_date'].iloc[0]
                    estimated_date = location_estimated_data[location_estimated_data['year'] == year]['flowering_prediction'].iloc[0]
                    difference = (observed_date - estimated_date).days
                                
                    if difference < 0:
                        difference = -difference
                else:
                    difference = None
                differs.append([location, year, difference])
            differs_df = pd.DataFrame(differs, columns = ['location', 'year', 'difference'])
        
        errors = []
        for location in location_list:
            differs_per_location = differs_df[differs_df['location'] == location]
            if not differs_per_location.empty:
                mae_per_location = round(np.mean(differs_per_location['difference']), 3)
                rmse_per_location = round(np.sqrt(np.mean(np.square(differs_per_location['difference']))), 3)
                errors.append([location, mae_per_location, rmse_per_location])
        errors_df = pd.DataFrame(errors, columns=['location', 'MAE', 'RMSE'])
        
        if sorting == True:
            filtered_df = errors_df[errors_df['location'].isin(location_list)].copy()
            sorted_df = filtered_df.sort_values(by=errortype, ascending=True).reset_index(drop=True)
            return sorted_df
        else:        
            return errors_df
    
    
    def calculate_accumulation(yearly_temperature_data, temperature_threshold, chill_requirement, heat_requirement, day_length, year):
        # set the start date of calculating chill days
        start_index = 0
        for index, row in yearly_temperature_data.iterrows():
            if row['minTa'] >= temperature_threshold:
                start_index += 1
            else:
                break
        
        pre_threshold_data = yearly_temperature_data.iloc[:start_index]
        yearly_temperature_data = yearly_temperature_data.iloc[start_index:].reset_index(drop=True)
            
        # calculate the accumulation of chill days
        yearly_temperature_data['chilldays'] = yearly_temperature_data.apply(lambda row: ChillDayFormula.calculate_chilldays(row, temperature_threshold), axis = 1)
        yearly_temperature_data['cd_accumulation'] = yearly_temperature_data['chilldays'].cumsum()
        
        # dormancy release date
        if (yearly_temperature_data['cd_accumulation'] <= chill_requirement).any():
            dormancy_release_date = yearly_temperature_data[yearly_temperature_data['cd_accumulation'] <= chill_requirement].iloc[0]['tm']
        elif (yearly_temperature_data[(yearly_temperature_data['tm'] >= f'{year}-01-31') & (yearly_temperature_data['ssDur'] >= day_length)]).any().any():
            dormancy_release_date = yearly_temperature_data[yearly_temperature_data['ssDur'] >= day_length].iloc[0]['tm']
        else:
            dormancy_release_date = None
        
        if dormancy_release_date is None:
            return None, None

        # calculate the accumulation of anti-chill days
        heat_data = yearly_temperature_data[yearly_temperature_data['tm'] > dormancy_release_date]
        heat_data['anti_chilldays'] = heat_data.apply(lambda row: ChillDayFormula.calculate_anti_chilldays(row, temperature_threshold), axis = 1)
        heat_data['anti_chilldays'] = heat_data['anti_chilldays'].apply(lambda x: x if x > 0 else 0)
        heat_data['acd_accumulation'] = heat_data['anti_chilldays'].cumsum()
        
        # find the calculated budburst date
        if (heat_data['acd_accumulation'] >= heat_requirement).any():
            flowering_date = heat_data[heat_data['acd_accumulation'] >= heat_requirement].iloc[0]['tm']
        else:
            flowering_date = None
        
        # make chill, heatdays list until dormancy release date
        if dormancy_release_date is None or flowering_date is None:
            return None, None
        else:
            cumulative_cd = [0] * len(pre_threshold_data)
            if dormancy_release_date is not None:
                for index, row in yearly_temperature_data.iterrows():
                    if row['tm'] <= dormancy_release_date:
                        cumulative_cd.append(row['cd_accumulation'])
            cumulative_acd = []
            edge_value = cumulative_cd[-1]
            cumulative_acd.append(edge_value)
            if flowering_date is not None:
                for index, row in heat_data.iterrows():
                    if row['tm'] > dormancy_release_date and row['tm'] <= flowering_date:
                        cumulative_acd.append(row['acd_accumulation'] + edge_value)
            
        return cumulative_cd, cumulative_acd
    
    def calculate_accumulation_application(temperature_data, location_list, temperature_threshold, chill_requirement, heat_requirement, min_obs, max_obs, csv_name = 'cumulative cd, acd list'):
        results = []
        for location in location_list:
            location_temperature_data = temperature_data[temperature_data['location'] == location]
            for year in range(min_obs, max_obs+1):
                start_date = datetime(year -1, 9, 1)
                end_date = datetime(year, 6, 1)
                yearly_temperature_data = location_temperature_data[(location_temperature_data['tm'] >= start_date) & (location_temperature_data['tm'] < end_date)]
                
                if not yearly_temperature_data.empty:
                    cumulative_cd, cumulative_acd = phenology_prediction.calculate_accumulation(yearly_temperature_data, temperature_threshold, chill_requirement, heat_requirement)
                    results.append((location, year, cumulative_cd, cumulative_acd))
        results_df = pd.DataFrame(results, columns=['location', 'year', 'cumulative_cd', 'cumulative_acd'])
        results_df.to_csv(f'{csv_name}.csv', index = False)
        return results_df       
        
        
    def calculate_accumulation_values(yearly_temperature_data, temperature_threshold, target_heat):
        # for calculating temperature time values
        cumulative_temps = [0]
        cumulative_temp = 0
            
        for _, row in yearly_temperature_data.iterrows():
            anti_chill = ChillDayFormula.calculate_anti_chilldays(row, temperature_threshold)
            cumulative_temp += anti_chill if anti_chill is not None else 0   
            cumulative_temps.append(cumulative_temp)
            if cumulative_temp >= target_heat:
                break
        return cumulative_temps
    
    def convert_to_array(data):
        if isinstance(data, (int, float)):
            return np.array([data])
        else:
            return np.array([float(i) for i in data.replace('[', '').replace(']', '').split(', ') if i])
                    
    def np_datetime64_to_datetime(dt64):
        if pd.isnull(dt64):
            return None
        timestamp = (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')
        return datetime.fromtimestamp(timestamp, tz = timezone.utc)
    
        
class phenology_clustering():
    def temperature_time_increment(directory1, directory2, phenology_data):
        temperature_time_increment_data = []
        accumulation = pd.read_csv(str(directory1), encoding= 'utf-8')
        predicted_data = pd.read_csv(str(directory2), encoding= 'utf-8')
        phenology_data['flowering_date'] = pd.to_datetime(phenology_data['flowering_date'], errors='coerce')
        predicted_data['flowering_prediction'] = pd.to_datetime(predicted_data['flowering_prediction'], errors='coerce')
        
        for location, locational_accumulation in accumulation.groupby('location'):
            for year, yearly_accumulation in locational_accumulation.groupby('year'):
                cumulative_cd = phenology_prediction.convert_to_array(yearly_accumulation['cumulative_cd'].values[0])
                cumulative_acd = phenology_prediction.convert_to_array(yearly_accumulation['cumulative_acd'].values[0])
                
                if len(cumulative_cd) == 0 or len(cumulative_acd) == 0:
                    print(f'Skipping {location}, {year} due to empty arrays')
                    continue
                
                cd_increments = [cumulative_cd[i+1] - cumulative_cd[i] for i in range(len(cumulative_cd) -1)]
                cd_increments = [x for x in cd_increments if not np.isnan(x)]
                acd_increments = [cumulative_acd[i+1] - cumulative_acd[i] for i in range(len(cumulative_acd) -1)]
                acd_increments = [x for x in acd_increments if not np.isnan(x)]
                
                combined_increments = cd_increments + acd_increments
                if len(combined_increments) < 120:
                    print(f'Skipping {location}, {year} due to insufficient increments')
                    continue
                
                flowering_date_df = phenology_data[(phenology_data['location'] == location) & (phenology_data['flowering_date'].dt.year == year)]
                flowering_date = None
                if not flowering_date_df.empty:
                    flowering_date = phenology_prediction.np_datetime64_to_datetime(flowering_date_df['flowering_date'].values[0])
                predicted_flowering_df = predicted_data[(predicted_data['location'] == location) & (predicted_data['flowering_prediction'].dt.year == year)]
                predicted_flowering_date = None
                if not predicted_flowering_df.empty:
                    predicted_flowering_date = phenology_prediction.np_datetime64_to_datetime(predicted_flowering_df['flowering_prediction'].values[0])
                
                diff = None
                if flowering_date and predicted_flowering_date:
                    diff = (predicted_flowering_date - flowering_date).days
                temperature_time_increment_data.append((location, year, combined_increments, diff))
        temperature_time_increment_df = pd.DataFrame(temperature_time_increment_data, columns=['location', 'year', 'temperature_time_vector', 'prediction_error'])
        temperature_time_increment_df.to_csv('temperature_time_increment.csv', index = False)
        return temperature_time_increment_df

    def hierarchical_clustering(directory1, directory2, phenology_data, method='ward'):
        # remain for errors in after...
        def safe_literal_eval(x):
            try:
                eval_list = literal_eval(x)
                if isinstance(eval_list, list):
                    return [elem for elem in eval_list if not pd.isna(elem) and elem is not None]
                else:
                    return []
            except(ValueError, SyntaxError):
                return []
        
        temperature_time_increment_df = phenology_clustering.temperature_time_increment(directory1, directory2, phenology_data)
        # temperature_time_increment_df['temperature_time_vector'] = temperature_time_increment_df['temperature_time_vector'].apply(safe_literal_eval)
        temperature_time_increment_df = temperature_time_increment_df[temperature_time_increment_df['temperature_time_vector'].apply(len) > 0]
        temperature_time_vector = temperature_time_increment_df['temperature_time_vector'].to_list()
        
        empty_rows = temperature_time_increment_df[temperature_time_increment_df['temperature_time_vector'].apply(len) == 0]
        print(f'Number of rows with empty lists: {len(empty_rows)}')
        
        # pading (matching the vector length as same)
        max_length = max(len(vec) for vec in temperature_time_vector)
        temperature_time_vector = [vec + [0] * (max_length - len(vec)) for vec in temperature_time_vector]
        temperature_time_increments = np.array(temperature_time_vector)
        
        # data scaling (with StandardScaler)
        scaler = StandardScaler()
        temperature_time_increment_scaled = scaler.fit_transform(temperature_time_increments)
        
        # do hierarchical clustering & plot dendrogram
        linked = linkage(temperature_time_increment_scaled, method = method)
        sys.setrecursionlimit(10000)
        plt.figure(figsize=(12,8))
        dendrogram(linked, orientation='top', distance_sort = 'descending', show_leaf_counts = True, leaf_font_size=0.01)
        plt.title('Dendrogram of Hierarchical Clustering of Temperature Time Vector of the Chill-Day Model', fontsize=75)
        plt.xlabel('Distance', fontsize=75)
        plt.ytikcs(fontsize=40)
        plt.show()
        return temperature_time_increment_df, temperature_time_increment_scaled
    
    def tsne_visualization(directory1, directory2, phenology_data, method = 'ward', representative_values = False, n_components = 2, random_states=150, perplexity=50, individual = False, alpha=0.8):
        temperature_time_increment_df, temperature_time_increment_scaled = phenology_clustering.hierarchical_clustering(directory1, directory2, phenology_data, method)
        linked = linkage(temperature_time_increment_scaled, method = method)
        
        max_distance = int(input("Set Your Clustering Criteria based on Hierarchical Clustering Plot (ex:28)"))
        clusters = fcluster(linked, max_distance, criterion = 'distance')
        temperature_time_increment_df['cluster'] = clusters
        
        cluster_counts = temperature_time_increment_df['cluster'].value_counts()
        print(f"Number of data points in each cluster: {cluster_counts}")
        
        # Dimension Shrinking with t-SNE
        tsne = TSNE(n_components=n_components, random_state=random_states, perplexity=perplexity)
        tsne_results = tsne.fit_transform(temperature_time_increment_scaled)
        for n in range(n_components):
            temperature_time_increment_df[f'tsne-{n+1}'] = tsne_results[:, n]
            
        cluster_df = {}
        for cluster in np.unique(clusters):
            cluster_df[f'cluster_{cluster}'] = temperature_time_increment_df[temperature_time_increment_df['cluster'] == cluster]
             
            if representative_values == True:
                print(f"\nCluster {cluster}")
                print(temperature_time_increment_df[temperature_time_increment_df['cluster'] == cluster].head(5))
            if n_components == 2 and individual == True:
                cluster_data = temperature_time_increment_df[temperature_time_increment_df['cluster'] == cluster]
                cluster_mae = temperature_time_increment_df.groupby('cluster')['prediction_error'].apply(lambda x: x.abs().mean()).reset_index()
                cluster_mae.columns = ['cluster', 'MAE']
                plt.figure(figsize=(8, 8))
                vmax = np.max(np.abs(cluster_data['prediction_error']))
                cmap = mcolors.LinearSegmentedColormap.from_list("blue_white_red", ["blue", "white", "red"])
                sns.scatterplot(x='tsne-1', y='tsne-2', hue='prediction_error', palette=cmap, data=cluster_data, s=100, alpha=alpha, hue_norm=(-vmax, vmax))
                plt.title(f'Prediction Error of Cluster {cluster}', fontsize=22)
                plt.xlabel('t-SNE Component 1', fontsize=20)
                plt.ylabel('t-SNE Component 2', fontsize=20)
                plt.legend(fontsize=15)
                for index, row in cluster_mae.iterrows():
                    cluster_id = row['cluster']
                    mae = row['MAE']
                    if cluster_id == index:
                        plt.text(0.4, 0.95, f'Cluster {int(cluster_id)} MAE: {mae: .2f}',
                                 transform=plt.gca().transAxes, fontsize=12, verticalalignment='top')
                plt.show()
                
        if n_components == 2:
            plt.figure(figsize=(12,8))
            sns.scatterplot(data=temperature_time_increment_df, x='tsne-1', y='tsne-2', hue='cluster', palette='deep', alpha=0.8)
            plt.title('t-SNE Visualization of Clustering Results', fontsize=24)
            plt.xlabel('t-SNE Component 1', fontsize=20)
            plt.ylabel('t-SNE Component 2', fontsize=20)
            plt.legend(title='Cluster')
            plt.show()
        elif n_components == 3:
            fig = plt.figure(figsize=(9,6))
            ax = fig.add_subplot(111, projection='3d')
            colors = sns.color_palette("hsv", len(cluster_df))
            for index, (cluster, df) in enumerate(cluster_df.items()):
                ax.scatter(df['tsne-1'], df['tsne-2'], df['tsne-3'],
                           color = colors[index], label=f'Cluster {index + 1}', alpha=alpha)
            ax.set_xlabel('t-SNE Component 1', fontsize=20)
            ax.set_ylabel('t-SNE Component 2', fontsize=20)
            ax.set_zlabel('t-SNE Component 3', fontsize=20)
            ax.legend(bbox_to_anchor=(1.1, 1), loc='upper left', fontsize=15)
            plt.title('3D t-SNE Visualization of Clustering Results', fontsize=24)
            plt.subplots_adjust(right=0.80)
            plt.show()
        else:
            print("Visualization of 4th Dimension is not supported in phenoloPy.")            
            print("\nPlease Check Your DataFrame.")
        temperature_time_increment_df.to_csv("clustered_temperature_time_increment_df.csv", index=False)
        return temperature_time_increment_df
    
                     
class phenology_visualization():
    def budburst_error_heatmap(parameterset_rmse_df, x_axis_size = 17, y_axis_size = 12, arrange = 1, figure_title = "Heatmap of RMSE Trend about para1, para2 in Phenology Prediction"):           # if you set your x-axis as first parameter, let arrange = 1
        plt.rcParams['figure.figsize'] = [x_axis_size, y_axis_size]
        plt.rcParams['xtick.minor.visible'] = False
        error_df = parameterset_rmse_df
        
        error_df_columns = error_df.columns
        if arrange == 1:
            error_df = error_df.pivot(index=error_df_columns[1], columns=error_df_columns[0], values=error_df_columns[2])
        elif arrange == 2:
            error_df = error_df.pivot(index=error_df_columns[0], columns=error_df_columns[1], values=error_df_columns[2])
        
        error_heatmap = sns.heatmap(error_df, cmap='YlGnBu', annot=True, fmt = '.2f')
        error_heatmap.set_xlabel(error_df.columns.name, fontsize=18)
        error_heatmap.set_ylabel(error_df.index.name, fontsize=18)
        plt.title(figure_title, fontsize=20)
        plt.show()
    
    def flowering_error_heatmap(parameterset_error_df, errortype = 'MAE', para1 = 'heat_requirement', para2 = 'chill_requriement', figure_title = "Heatmap of MAE Trend about Cr & Hr in Flowering Date Prediction"):
        plt.rcParams['xtick.minor.visible'] = False
        error_df = parameterset_error_df
        error_df = error_df.groupby([para1, para2])[errortype].min().reset_index()
        error_df = error_df.pivot(index=para1, columns=para2, values=errortype)
        error_df = sns.heatmap(error_df, cmap='YlGnBu', annot=True, fmt='.2f')
        plt.title(figure_title, fontsize=13)
        plt.xlabel(para2, fontsize=15)
        plt.ylabel(para1, fontsize=15)
        plt.show()
    
    
    def flowering_error_contourmap(parameterset_error_df, errortype = 'MAE', para1 = 'heat_requirement', para2 = 'chill_requirement', label1 = "Heat_Requirement(Hr)", label2 = "Chill-Requirement(Cr)", label3 = "Minimum Mean Absolute Error(MAE) of Tc for Cr & Hr combinations"):         # error type is MAE or RMSE   # para1/2 is your y-axis, x-axis column name
        # data preprocessing 
        error_df = parameterset_error_df
        error_df = error_df.groupby([para1, para2])[errortype].min().reset_index()
        error_df = error_df.pivot(index = para1, columns = para2, values = errortype)
        
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['xtick.minor.visible'] = False
        size = 100
        x = np.linspace(np.min(error_df.columns), np.max(error_df.columns), size)
        y = np.linspace(np.min(error_df.index), np.max(error_df.index), size)
        
        X, Y = np.meshgrid(x, y)
        f = RegularGridInterpolator((error_df.index.values, error_df.columns.values), error_df.values, method='linear')
        points = np.array([Y.ravel(), X.ravel()]).T
        Z = f(points).reshape(Y.shape)

        fig = plt.figure(figsize = (12, 8))
        fig.set_facecolor('white')
        ax = fig.add_subplot()
        contour1 = ax.contour(X, Y, Z, levels=10, colors='k', linewidths = 1, linestyles = '--')
        contour2 = ax.contourf(X, Y, Z, levels=256, cmap = 'jet')
        
        ax.clabel(contour1, contour1.levels, inline=True)
        ax.set_xlabel(label2, fontsize=16)
        ax.set_ylabel(label1, fontsize=16)
        cbar = fig.colorbar(contour2, shrink=0.9)
        cbar.set_label(label3, fontsize=14)
        
        plt.tight_layout()
        plt.show()
        
        
    def comparing_linegraph(errors_df, bestfit_directory, phenology_data, target_location_list):
        observed_data = phenology_data[['location', 'flowering_date']]
        estimated_data = pd.read_csv(bestfit_directory, encoding = 'utf-8')
        
        for location in target_location_list:
            observed_in_location = observed_data[observed_data['location'] == location]
            observed_in_location = observed_in_location['flowering_date'].to_string().split()[1::2]
            observed_flowering_date = pd.to_datetime(observed_in_location, errors= 'coerce')
            observed_flowering_days = (observed_flowering_date - pd.to_datetime(observed_flowering_date.year, format='%Y')).days
            estimated_in_location = estimated_data[estimated_data['location'] == location]
            estimated_in_location = estimated_in_location['flowering_prediction'].to_string().split()[1::2]
            estimated_flowering_date = pd.to_datetime(estimated_in_location, errors= 'coerce')
            estimated_flowering_days = (estimated_flowering_date - pd.to_datetime(estimated_flowering_date.year, format='%Y')).days
                
            observed_flowering = pd.DataFrame({'year': observed_flowering_date.year, 'flowering_days': observed_flowering_days}).dropna().astype(int)
            estimated_flowering = pd.DataFrame({'year': estimated_flowering_date.year, 'flowering_days': estimated_flowering_days}).dropna().astype(int)
                
            common_years = observed_flowering['year'].isin(estimated_flowering['year'])
            observed_flowering = observed_flowering[common_years]
            common_years = estimated_flowering['year'].isin(observed_flowering['year'])
            estimated_flowering = estimated_flowering[common_years]
            
            merged_data = pd.merge(observed_flowering, estimated_flowering, on='year', suffixes=('_observed', '_predicted'))
                
            x_axis = merged_data['year']
            y_axis_1 = merged_data['flowering_days_observed']
            y_axis_2 = merged_data['flowering_days_predicted']
                
            plt.figure(figsize=(8, 6))
            plt.rcParams['xtick.minor.visible'] = True
            plt.rcParams['xtick.major.size'] = 2
            plt.plot(x_axis, y_axis_1, label= "Observed", linestyle='--', color='k', marker='o', markersize=5, markerfacecolor='none', alpha=0.7)
            plt.plot(x_axis, y_axis_2, label= "Predicted", linestyle='-', color='k', marker='o', markersize=5, alpha=0.7)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            plt.xlabel('Year', fontsize = 16)
            plt.ylabel('Flowering Days from 1/1', fontsize = 16)
            plt.title(f'Flowering Date of {location} (Observed vs Predicted)', fontsize=18)
            plt.ylim(min(y_axis_1.min(), y_axis_2.min())-15, max(y_axis_1.max(), y_axis_2.max())+10)
            plt.legend(fontsize=14, facecolor='none', frameon = False)
            plt.grid(axis='y')
            
            ax = plt.gca()
            ax.xaxis.set_major_locator(MultipleLocator(4))
            textstr = f'MAE = {errors_df[errors_df["location"] == location]["MAE"].values[0]}\nRMSE = {errors_df[errors_df["location"] == location]["RMSE"].values[0]}'
            plt.text(x_axis.max()+1, min(y_axis_1.min(), y_axis_2.min())-10, textstr, fontsize=13, verticalalignment='bottom', horizontalalignment='right')   # bbox=dict(facecolor='white', alpha=0.5)
            plt.show()

    
    def simple_regression(bestfit_directory, previous_directory, phenology_data, fig_title = 'Simple Linear Regression with Observed & Predicted Flowering Dates', color = 'black'):
        observed_data = phenology_data[['location', 'flowering_date']]
        estimated_data = pd.read_csv(bestfit_directory, encoding = 'utf-8')
        estimated_data = estimated_data[['location', 'year', 'flowering_prediction']]
        previous_res_data = pd.read_csv(previous_directory, encoding = 'utf-8')
        previous_res_data = previous_res_data[['location', 'year', 'flowering_prediction']]
        
        observed_data['flowering_date'] = pd.to_datetime(observed_data['flowering_date'], errors='coerce')
        observed_data['year'] = observed_data['flowering_date'].dt.year
        observed_data = observed_data.dropna(subset=['flowering_date'])
        estimated_data['flowering_prediction'] = pd.to_datetime(estimated_data['flowering_prediction'], errors='coerce')
        estimated_data = estimated_data.dropna(subset=['flowering_prediction'])
        previous_res_data['flowering_prediction'] = pd.to_datetime(previous_res_data['flowering_prediction'], errors='coerce')
        previous_res_data = previous_res_data.dropna(subset=['flowering_prediction'])

        # merge data
        merged_data = pd.merge(observed_data, estimated_data, left_on=['location', 'year'], right_on=['location', 'year'])
        merged_prev = pd.merge(observed_data, previous_res_data, left_on=['location', 'year'], right_on=['location', 'year'], how='inner')

        observed_flowering_days = merged_data['flowering_date'].dt.dayofyear
        estimated_flowering_days = merged_data['flowering_prediction'].dt.dayofyear
        
        observed_prev_days = merged_prev['flowering_date'].dt.dayofyear
        previous_flowering_days = merged_prev['flowering_prediction'].dt.dayofyear

        # linear regression
        reg_new = LinearRegression().fit(observed_flowering_days.values.reshape(-1,1), estimated_flowering_days.values.reshape(-1, 1))
        slope = reg_new.coef_[0][0]
        intercept = reg_new.intercept_[0]
        r2_new = reg_new.score(observed_flowering_days.values.reshape(-1,1), estimated_flowering_days.values.reshape(-1, 1))
        r_new = np.sqrt(r2_new)
        
        # linear regression for previous results
        reg_prev = LinearRegression().fit(observed_prev_days.values.reshape(-1,1), previous_flowering_days.values.reshape(-1, 1))
        slope_prev = reg_prev.coef_[0][0]
        intercept_prev = reg_prev.intercept_[0]
        r2_prev = reg_prev.score(observed_prev_days.values.reshape(-1,1), previous_flowering_days.values.reshape(-1, 1))
        r_prev = np.sqrt(r2_prev)

        # visualization
        plt.rcParams['xtick.minor.visible'] = False
        plt.figure(figsize=(8, 8))
        jitter_strength = 1.0
        obs_new_j = observed_flowering_days + np.random.normal(0, jitter_strength, size=observed_flowering_days.shape)
        estimated_flowering_days_jitter = estimated_flowering_days + np.random.normal(0, jitter_strength, size=estimated_flowering_days.shape)
        obs_prev_j = observed_prev_days + np.random.normal(0, jitter_strength, size=observed_prev_days.shape)
        prev_j = previous_flowering_days + np.random.normal(0, jitter_strength, size=previous_flowering_days.shape)

        plt.scatter(obs_new_j, estimated_flowering_days_jitter, color='black', alpha=0.6, label='Refined Model')
        
        x_grid_min = int(min(observed_flowering_days.min(), observed_prev_days.min()))
        x_grid_max = int(max(observed_flowering_days.max(), observed_prev_days.max()))
        x_grid = np.linspace(x_grid_min, x_grid_max, 200).reshape(-1, 1)
        
        y_line_prev = reg_prev.predict(x_grid).ravel()
        y_line_new = reg_new.predict(x_grid).ravel()
        
        if bestfit_directory != previous_directory:
            plt.plot(x_grid, y_line_prev, linestyle='-', color=color, alpha=0.9, label=f'Previous fit: $R$={r_prev:.2f}')
        plt.plot(x_grid, y_line_new, linestyle='-', color='black', alpha=0.8, label=f'New fit: $R$={r_new:.2f}')
        plt.plot([x_grid_min, x_grid_max], [x_grid_min, x_grid_max], color='grey', linestyle='--', linewidth=1.2, alpha=0.9, label='y=x')
        
        ticks = np.arange(x_grid_min, x_grid_max + 1, 7)
        plt.xticks(ticks=ticks, labels=pd.to_datetime(ticks, format='%j').strftime('%m-%d'), fontsize=14)
        plt.yticks(ticks=ticks, labels=pd.to_datetime(ticks, format='%j').strftime('%m-%d'), fontsize=14)
        plt.xlabel('Observed Flowering Date', fontsize=20)
        plt.ylabel('Predicted Flowering Date', fontsize=20)
        plt.title(fig_title, fontsize=24)
        plt.legend(frameon=True, fontsize=16)
        plt.grid(True)
        plt.tight_layout()
        plt.show()


    def chillday_graph_individual(directory, years_per_page = 1):
        accumulation = pd.read_csv(str(directory), encoding= 'utf-8')
        # iterate through each location group
        for location, locational_accumulation in accumulation.groupby('location'):
            mypdf = PdfPages(f'ChillDay Model graph in {location}.pdf')
            
            yearly_data = list(locational_accumulation.groupby('year'))
            num_pages = (len(yearly_data) + years_per_page - 1) // years_per_page
            
            for page in range(num_pages):
                fig, axes = plt.subplots(years_per_page, 1, figsize = (8, 5 * years_per_page), constrained_layout=True)
                if years_per_page == 1:
                    axes = [axes]
                else:
                    axes = axes.flatten()
                
                page_data = yearly_data[page * years_per_page:(page + 1) * years_per_page]

                for index, (year, yearly_accumulation) in enumerate(page_data):
                    if index >= len(axes):
                        continue
                    
                    ax = axes[index]
                    try:
                        cumulative_cd = phenology_prediction.convert_to_array(yearly_accumulation['cumulative_cd'].values[0])
                        cumulative_acd = phenology_prediction.convert_to_array(yearly_accumulation['cumulative_acd'].values[0])
                    except Exception as e:
                        print(f"Error processing year {year} in location {location}: {e}")
                        continue
                    
                    if cumulative_cd.size == 0 and cumulative_acd.size == 0:
                        print(f"Skipping year {year} in location {location} due to empty arrays")
                        continue

                    x1 = np.arange(1, len(cumulative_cd) + 1) if cumulative_cd.size > 0 else np.array([])
                    x2_start = len(cumulative_cd) if cumulative_cd.size > 0 else 0
                    x2 = np.arange(x2_start, x2_start + len(cumulative_acd)) if cumulative_acd.size > 0 else np.array([])
                
                    ax = axes[index]
                    if x1.size > 0:
                        ax.plot(x1, cumulative_cd, label = 'cumulative chilldays', color = 'blue')
                    if x2.size > 0:
                        ax.plot(x2, cumulative_acd, label = 'cumulative anti-chilldays', color = 'red')
                    ax.axhline(0, color='black', linestyle='-', linewidth=0.8, alpha=0.6)
                    
                    x_data_min = 1
                    x_data_max = x2[-1] if x2.size > 0 else (x1[-1] if x1.size > 0 else 1)
                    
                    month_labels = ['Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr']
                    num_ticks = len(month_labels)
                    
                    if x_data_max > x_data_min:
                        tick_positions = np.linspace(x_data_min, x_data_max, num_ticks)
                        ax.set_xtics(tick_positions)
                        ax.set_xticlabels(month_labels, fontsize = 13)
                    else:
                        ax.set_xticks([x_data_min])
                        ax.set_xticklabels([month_labels[0]], fontsize=13)
                    ax.tick_params(axis='y', labelsize=13)

                    ax.set_xlabel('Calendar Time (Month)', fontsize=17)
                    ax.set_ylabel('Thermal Time', fontsize=17)
                    ax.legend(loc = 'lower left', fontsize=13)
                
                num_plots_on_page = len(page_data)
                for i in range(num_plots_on_page, len(axes)):
                    if i < len(fig.axes) and axes[i] in fig.axes:
                        fig.delaxes(axes[i])
                try:
                    mypdf.savefig(fig)
                except Exception as e:
                    print(f"Error saving page {page+1} for {location}: {e}")
                plt.close(fig)
            mypdf.close()


    def detailed_chillday_graph(directory1, directory2, temperature_data, phenology_data, temperature_threshold, target_heat, years_per_page, frameon=True):
        phenology_data['flowering_date'] = pd.to_datetime(phenology_data['flowering_date'], errors='coerce')
        phenology_data['bud_burst_date'] = pd.to_datetime(phenology_data['bud_burst_date'], errors='coerce')

        # convert 'date' columns to UTC form
        if phenology_data['flowering_date'].dt.tz is None:
            phenology_data['flowering_date'] = phenology_data['flowering_date'].dt.tz_localize('UTC')
        else:
            phenology_data['flowering_date'] = phenology_data['flowering_date'].dt.tz_convert('UTC')

        if phenology_data['bud_burst_date'].dt.tz is None:
            phenology_data['bud_burst_date'] = phenology_data['bud_burst_date'].dt.tz_localize('UTC')
        else:
            phenology_data['bud_burst_date'] = phenology_data['bud_burst_date'].dt.tz_convert('UTC')

        accumulation = pd.read_csv(str(directory1), encoding= 'utf-8')
        for location, locational_accumulation in accumulation.groupby('location'):
            mypdf = PdfPages(f'ChillDay Model Observed vs Predicted in {location}.pdf')

            yearly_data = list(locational_accumulation.groupby('year'))
            num_pages = (len(yearly_data) + years_per_page - 1) // years_per_page

            for page in range(num_pages):
                fig, axes = plt.subplots(years_per_page, 1, figsize=(8, 5 * years_per_page), constrained_layout=True)
                if years_per_page == 1:
                    axes = [axes]

                plot_needed = False

                for index, (year, yearly_accumulation) in enumerate(
                    yearly_data[page * years_per_page:(page + 1) * years_per_page]
                ):

                    # predicted data
                    predicted_flowering_df = pd.read_csv(str(directory2), encoding='utf-8')
                    predicted_flowering_df['flowering_prediction'] = pd.to_datetime(predicted_flowering_df['flowering_prediction'], errors='coerce')

                    if predicted_flowering_df['flowering_prediction'].dt.tz is None:
                        predicted_flowering_df['flowering_prediction'] = predicted_flowering_df['flowering_prediction'].dt.tz_localize('UTC')
                    else:
                        predicted_flowering_df['flowering_prediction'] = predicted_flowering_df['flowering_prediction'].dt.tz_convert('UTC')

                    predicted_flowering_df = predicted_flowering_df[(predicted_flowering_df['location'] == location) & (predicted_flowering_df['flowering_prediction'].dt.year == year)]

                    if predicted_flowering_df.empty:
                        continue

                    cumulative_cd = phenology_prediction.convert_to_array(yearly_accumulation['cumulative_cd'].values[0])
                    cumulative_acd = phenology_prediction.convert_to_array(yearly_accumulation['cumulative_acd'].values[0])
                    x1 = np.arange(1, len(cumulative_cd) + 1)
                    x2 = np.arange(len(cumulative_cd), len(cumulative_cd) + len(cumulative_acd))

                    ax = axes[index]
                    ax.plot(x1, cumulative_cd, label='Predicted Chilldays', color='blue')
                    ax.plot(x2, cumulative_acd, label='Predicted Anti-Chilldays', color='red')
                    ax.axvline(x=x1[-1], color='blue', linestyle='dotted', linewidth=1.25, ymin=0, ymax=0.05)
                    ax.scatter(x1[-1], cumulative_cd[-1], color='blue', zorder=5)
                    ax.text(x1[-1]-1, cumulative_cd[-1]-1, 'CDM Dormancy-Release', fontsize=10, color='blue', ha='right', va='top')
                    if len(cumulative_acd) > 0:
                        ax.plot(x2, cumulative_acd, color='red')
                        ax.axvline(x=x2[-1], color='red', linestyle='dotted', linewidth=1.25, ymin=0, ymax=1)
                        ax.scatter(x2[-1], cumulative_acd[-1], color='red', zorder=5)
                        ax.text(x2[-1]-1, cumulative_acd[-1]-1, 'CDM Bloom', fontsize=10, color='red', ha='right', va='top')
                        
                    plt.xlabel(f'Days of Year (Starting from {year-1}/09/01)', fontsize=12)
                    plt.ylabel('Temperature Time', fontsize=12)
                    plt.title(f'ChillDay Model Graph Observed vs Predicted in {location}, {year}', fontsize=14)
                    plt.axhline(color='black', linestyle='dotted', linewidth=1.5, alpha=0.4)

                    # observed data
                    observed_data = None
                    location_temperature_data = temperature_data[temperature_data['location'] == location]
                    end_date = datetime(year, 6, 1, tzinfo=timezone.utc)
                    start_date = datetime(year - 1, 9, 1, tzinfo=timezone.utc)
                    location_temperature_data['tm'] = pd.to_datetime(location_temperature_data['tm'], errors='coerce')

                    if location_temperature_data['tm'].dt.tz is None:
                        location_temperature_data['tm'] = location_temperature_data['tm'].dt.tz_localize('UTC')
                    else:
                        location_temperature_data['tm'] = location_temperature_data['tm'].dt.tz_convert('UTC')

                    yearly_temperature_data = location_temperature_data[(location_temperature_data['tm'] <= end_date) & (location_temperature_data['tm'] >= start_date)]
                
                    flowering_date_df = phenology_data[(phenology_data['location'] == location) & 
                                   (phenology_data['bud_burst_date'].dt.year == year) & 
                                   (phenology_data['flowering_date'].dt.year == year)]

                    if flowering_date_df.empty:
                        continue
                    if not flowering_date_df.empty:
                        flowering_date_np = flowering_date_df['flowering_date'].values[0]
                        flowering_date = phenology_prediction.np_datetime64_to_datetime(flowering_date_np)
                        bud_burst_date_np = flowering_date_df['bud_burst_date'].values[0]
                        bud_burst_date = phenology_prediction.np_datetime64_to_datetime(bud_burst_date_np)
                        if bud_burst_date.year != flowering_date.year:
                            continue
                        if pd.notnull(bud_burst_date) and pd.notnull(flowering_date):
                            yearly_temperature_data = yearly_temperature_data[(yearly_temperature_data['tm'] >= bud_burst_date) & (yearly_temperature_data['tm'] <= flowering_date)]
                        else:
                            continue 
                        
                        if bud_burst_date and flowering_date:
                            observed_data = phenology_prediction.calculate_accumulation_values(yearly_temperature_data, temperature_threshold, target_heat)
                            observed_data = np.array(observed_data)
                            
                            if observed_data[-1] > target_heat:
                                extended_observed_data = np.append(observed_data, observed_data[-1])
                            else:
                                extended_observed_data = np.append(observed_data, target_heat)
                            x_observed_end = (flowering_date - datetime(year - 1, 9, 1, tzinfo=timezone.utc)).days + 1
                            x_observed = np.arange(x_observed_end - len(extended_observed_data) + 1, x_observed_end + 1)
                            ax.plot(x_observed, extended_observed_data, color='black', alpha=0.8, label = 'Observed Data')
                            ax.axvline(x=x_observed[-1], color='black', linestyle='dotted', linewidth=1.25, alpha=1, ymin=0, ymax = 1)
                            ax.scatter(x_observed[0], 0, color='black', zorder = 3, alpha=0.7)
                            ax.scatter(x_observed[-1], extended_observed_data[-1], color='black', zorder=3, alpha=0.7)
                            ax.text(x_observed[0]-18, -3, 'Bud-Burst', fontsize=10, color='green', ha='left', va='top')
                            
                            plot_needed = True
                        else:
                            print(f"Missing data for {location}, {year}")

                    if not predicted_flowering_df.empty:
                        predicted_flowering_date_np = predicted_flowering_df['flowering_prediction'].values[0]
                        predicted_flowering_date = phenology_prediction.np_datetime64_to_datetime(predicted_flowering_date_np)
                        if predicted_flowering_date and flowering_date:
                            diff = (predicted_flowering_date - flowering_date).days
                        else:
                            diff = None
                        ax.text(0.5, 0.95, f'Error = {diff}', transform=ax.transAxes, fontsize=12, color='black', ha='center', va='top', alpha=0.8)
                        plot_needed = True
                    
                    plt.legend(loc='lower left', frameon=frameon, fontsize=9)
                for index in range(len(yearly_data[page * years_per_page:(page+1) * years_per_page]), years_per_page):
                    fig.delaxes(axes[index]) 
                if plot_needed:
                    mypdf.savefig(fig)
                plt.close(fig)

            mypdf.close()
                
                           
    def chillday_graph_merged(directory1, directory2, alpha=0.15):
        clustered_temperature_time_increment_df = pd.read_csv(str(directory1), encoding='utf-8')
        cumulative_cd_acd_list = pd.read_csv(str(directory2), encoding='utf-8')
        cumulative_data = cumulative_cd_acd_list[['location', 'year', 'cumulative_cd', 'cumulative_acd']]
        clustered_temperature_time_increment_df = clustered_temperature_time_increment_df.merge(cumulative_data, on = ['location', 'year'])
        
        for cluster, cluster_df in clustered_temperature_time_increment_df.groupby('cluster'):
            pdf_name = f'Predicted ChillDay Model Cluster {cluster} in Merged.pdf'
            with PdfPages(pdf_name) as pdf:
                fig, ax = plt.subplots()
                
                all_cumulative_cd, all_cumulative_acd, all_cumulative = [], [], []
                first_plot_cd, first_plot_acd = True, True
                
                for _, row in cluster_df.iterrows():
                    location = row['location']
                    year = row['year']
                    cumulative_cd = phenology_prediction.convert_to_array(row['cumulative_cd'])
                    cumulative_acd = phenology_prediction.convert_to_array(row['cumulative_acd'])
                    
                    all_cumulative_cd.append(cumulative_cd)
                    all_cumulative_acd.append(cumulative_acd)
                    cumulative = np.concatenate((cumulative_cd, cumulative_acd))
                    all_cumulative.append(cumulative)

                    x = np.arange(len(cumulative))
                    x1, x2 = np.arange(len(cumulative_cd)), np.arange(len(cumulative_cd), len(cumulative_cd) + len(cumulative_acd))
                    ax.plot(x1, cumulative_cd, color='blue', alpha = alpha, label='Temperature Time Accumulation until Chill-Requirement' if first_plot_cd else "")
                    ax.plot(x2, cumulative_acd, color = 'red', alpha = alpha, label = 'Temperature Time Accumulation until Heat-Requirement after Chill-Requirement' if first_plot_acd else "")
                    
                    first_plot_cd, first_plot_acd = False, False

                max_length = max(len(c) for c in all_cumulative)
                padded_cumulative = np.array([np.pad(c, (0, max_length - len(c)), 'constant', constant_values=np.nan) for c in all_cumulative])
                mean_temperature_time_values = np.nanmean(padded_cumulative, axis=0)
                ax.plot(np.arange(len(mean_temperature_time_values)), mean_temperature_time_values, color='black', linewidth=2, label='Average Temperature Time across all Observations')
                
                cluster_mae = cluster_df['prediction_error'].abs().mean()
                cluster_error_mean = cluster_df['prediction_error'].mean()
                ax.text(0.1, 0.35, f'Cluster {cluster}\nMAE: {cluster_mae:.2f}\nME: {cluster_error_mean:.2f}', transform=ax.transAxes, fontsize=16, verticalalignment='top')
                ax.set_xlabel('Days from 09/01', fontsize = 16)
                ax.set_ylabel('Temperature Time', fontsize = 16)
                ax.set_title(f'Predicted ChillDay Model with Prediction Error of Cluster {cluster}', fontsize = 16)
                ax.grid(axis='y')
                ax.legend(fontsize=12, loc='center left', bbox_to_anchor=(1, 0.5))
                pdf.savefig(fig, bbox_inches = 'tight')
                plt.close(fig)
        print('Merged ChillDay Model Graph file created successfully.')
    
    
    def prediction_error_shift(temperature_time_increment_df, location = "Seoul", start_year = 1974, end_year = 2024, use_abs = True):
        el_set = set(el_nino_years)
        la_set = set(la_nina_years)
        enso_set = el_set | la_set

        locational_data = temperature_time_increment_df[(temperature_time_increment_df['location'] == location) & (temperature_time_increment_df['year'].between(start_year, end_year))].copy()

        if use_abs:
            locational_data['abs_prediction_error'] = np.abs(locational_data['prediction_error'].to_numpy())
        else:
            locational_data['abs_prediction_error'] = locational_data['prediction_error'].to_numpy()

        locational_data.sort_values('year', inplace=True)

        plt.figure(figsize=(16, 8))
        plt.plot(locational_data['year'], locational_data['abs_prediction_error'], label=("Absolute Prediction Error" if use_abs else "Prediction Error"),color='black', zorder=1, linewidth=1.5, alpha=0.75)

        first_plot_El, first_plot_La = True, True
        for year in sorted(el_set):
            if year in locational_data['year'].values:
                plt.scatter(year,locational_data.loc[locational_data['year'] == year, 'abs_prediction_error'], color='red', marker='*', s=100, zorder=2, label='El Nino' if first_plot_El else "", edgecolors='black')
                first_plot_El = False
        for year in sorted(la_set):
            if year in locational_data['year'].values:
                plt.scatter(year, locational_data.loc[locational_data['year'] == year, 'abs_prediction_error'], color='blue', marker='^', s=100, zorder=3, label='La Nina' if first_plot_La else "", edgecolors='black')
                first_plot_La = False

        non_event_years = locational_data[~locational_data['year'].isin(enso_set)]
        el_nino_event_years = locational_data[locational_data['year'].isin(el_set)]
        la_nina_event_years = locational_data[locational_data['year'].isin(la_set)]

        non_event_mean = non_event_years['abs_prediction_error'].mean()
        el_nino_mean = el_nino_event_years['abs_prediction_error'].mean()
        la_nina_mean = la_nina_event_years['abs_prediction_error'].mean()

        plt.axhline(y=non_event_mean, color='gray', linestyle='--', linewidth=1.2, label=f'Non Event Years Mean: {non_event_mean:.2f}', zorder=0, alpha=0.8)
        plt.axhline(y=el_nino_mean, color='red', linestyle='--', linewidth=1.2, label=f'El Niño Years Mean: {el_nino_mean:.2f}', zorder=0, alpha=0.8)
        plt.axhline(y=la_nina_mean, color='blue', linestyle='--', linewidth=1.2, label=f'La Niña Years Mean: {la_nina_mean:.2f}', zorder=0, alpha=0.8)

        yearly_mean_df = (locational_data.groupby('year', as_index=False)['abs_prediction_error'].mean().rename(columns={'abs_prediction_error': 'year_mean'}))

        def enso_label(y):
            if y in el_set: return "El Nino"
            if y in la_set: return "La Nina"
            return "Neutral"
        yearly_mean_df['ENSO'] = yearly_mean_df['year'].apply(enso_label)

        x_el = yearly_mean_df.loc[yearly_mean_df['ENSO'] == 'El Nino', 'year_mean'].to_numpy()
        x_la = yearly_mean_df.loc[yearly_mean_df['ENSO'] == 'La Nina', 'year_mean'].to_numpy()
        x_neu = yearly_mean_df.loc[yearly_mean_df['ENSO'] == 'Neutral', 'year_mean'].to_numpy()

        def permutation_pvalue(x, y, B=30000, seed=7):
            rng = np.random.default_rng(seed)
            x = np.asarray(x, float); y = np.asarray(y, float)
            if x.size == 0 or y.size == 0:
                return np.nan, np.nan, (x.size, y.size)
            obs = x.mean() - y.mean()
            concat = np.concatenate([x, y])
            n = x.size
            cnt = 0
            for _ in range(B):
                rng.shuffle(concat)
                d = concat[:n].mean() - concat[n:].mean()
                if np.abs(d) >= np.abs(obs):
                    cnt += 1
            p = (cnt + 1) / (B + 1)
            return obs, p, (x.size, y.size)

        def fmt_p(p):
            if np.isnan(p): return "NA"
            if p < 0.001: return "<0.001"
            return f"{p:.3f}"

        diff_el_neu, p_el_neu, (n_el, n_neu) = permutation_pvalue(x_el, x_neu)
        diff_la_neu, p_la_neu, (n_la, _)     = permutation_pvalue(x_la, x_neu)

        txt = (
            f"Permutation test (yearly mean, {start_year}–{end_year})\n"
            f"El Niño (n={n_el}) − Neutral (n={n_neu}): p={fmt_p(p_el_neu)}\n"
            f"La Niña (n={n_la}) − Neutral (n={n_neu}): p={fmt_p(p_la_neu)}"
        )   # : Δ={np.nan if np.isnan(diff_el_neu) else round(diff_el_neu,2)},
        ax = plt.gca()
        ax.text(0.01, 0.97, txt, transform=ax.transAxes, va='top', ha='left', fontsize=18,
                bbox=dict(boxstyle='round', facecolor='white', alpha=0.75, edgecolor='none'))

        plt.title(f"Prediction Error Shift in {location} in El Niño & La Niña Years.", fontsize=26)
        plt.xlabel('Year', fontsize=16)
        plt.ylabel('Absolute Prediction Error' if use_abs else 'Prediction Error', fontsize=24)
        if not locational_data.empty:
            plt.xticks(np.arange(max(start_year, int(locational_data['year'].min())),
                                int(locational_data['year'].max()) + 1, 5), fontsize=12)
        plt.xticks(fontsize=20)
        plt.yticks(fontsize=20)
        plt.legend(fontsize=22, loc='upper left', bbox_to_anchor=(1, 1))
        plt.scatter([], [], color='red', marker='*', s=100, label='El Niño')
        plt.scatter([], [], color='blue', marker='^', s=100, label='La Niña')
        plt.grid(True)
        plt.tight_layout()
        plt.show()
