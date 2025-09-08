##### requirements #####
import requests
from bs4 import BeautifulSoup
import pandas as pd # type: ignore
from .Variables import stn_dict, elemId, elemId_u

class phenology_preprocessing():
    def fetch_weather_data(start_date, end_date, stn_Id, API_Key):          
        Call_back_URL = "http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList"
        service_key = "?serviceKey={API}".format(API = API_Key)
        detail = f"&numOfRows=730&pageNo=1&dataCd=ASOS&dateCd=DAY&startDt={start_date}&endDt={end_date}&stnIds={stn_Id}"
        
        URL = Call_back_URL + service_key + detail
        
        rq = requests.get(URL)
        soup = BeautifulSoup(rq.text, "html.parser")
        
        weather_list = []
        for item in soup.find_all("item"):
            weather_sublist = []
            for Id in elemId:
                element = item.find(Id)
                if element is not None:
                    weather_sublist.append(element.text)
                else:
                    weather_sublist.append(None)
            weather_list.append(weather_sublist)
        
        return weather_list

    def download_weather_data(start_year, end_year, API_Key, details = True):
        interval_years=2
        
        if end_year == 2025:
            date = str(input("When is the end date you want to get? (ex: 0101)"))
        
        all_weather_data_df = list(range(95))
        for index, (location_kor, stn_id) in enumerate(stn_dict.items()):
            all_weather_data = []
            for start in range(start_year, end_year + 1, interval_years):
                end = start + interval_years - 1
                if end > end_year:
                    end = end_year
                start_date = f"{start}0101"
                
                if end == 2025:
                    end_date = f"2025{date}"
                else:
                    end_date = f"{end}1231"
                
                weather_data = phenology_preprocessing.fetch_weather_data(start_date, end_date, str(stn_id['id']), API_Key)
                all_weather_data.extend(weather_data)
            
            weather_df = pd.DataFrame(all_weather_data, columns = elemId_u)
            weather_df.insert(0, 'location', stn_id['name_en'])
            weather_df['tm'] = pd.to_datetime(weather_df['tm'], errors='coerce')
            weather_df.insert(weather_df.columns.get_loc('tm') + 1, 'year', weather_df['tm'].dt.year)
            all_weather_data_df[index] = weather_df
            
            if details == True:
                # create JSON file
                json_data = weather_df.to_json(orient='records', force_ascii=False, lines=True)
                with open(f"weather_data_{stn_id['name_en']}.json", 'w', encoding='utf-8') as json_file:
                    json_file.write(json_data)
                # create CSV file
                weather_df.to_csv(f"weather_{stn_id['name_en']}.csv", index=False)
                
            print(f"Data for {stn_id['name_en']} has been created successfully.")
        processed_all_weather_data_df = pd.concat(all_weather_data_df)
        processed_all_weather_data_df.to_csv("new_daily_meteorological_data.csv", index = False)
        print('All Data has been created successfully.')
        
    def merge_weather_data(directory1, directory2):
        old_data = pd.read_csv(str(directory1), encoding='utf-8')
        new_data = pd.read_csv(str(directory2), encoding='utf-8')
        old_data['tm'] = pd.to_datetime(old_data['tm'], errors='coerce')
        new_data['tm'] = pd.to_datetime(new_data['tm'], errors='coerce')
        
        common_columns = old_data.columns
        filtered_new_data = new_data[common_columns.intersection(new_data.columns)]
        
        merged_data = pd.concat([old_data, filtered_new_data]).drop_duplicates(subset=['location'] + ['tm'], keep='first')
        merged_data = merged_data.sort_values(by=['location'] + ['tm'])
        merged_data.to_csv(str(directory1), index=False, encoding='utf-8')
        print("New Data updated successfully.")
        
    def processing_phenology_data(directory1, plant_dict, new = False):
        new_phenology_data = pd.read_csv(str(directory1), encoding='CP949')
        plant_list = list(plant_dict.keys())
        
        for plant in plant_list:
            phenology_df = list(range(95))
            
            for index, (location, stn_id) in enumerate(stn_dict.items()):
                plant_data = ['', '', '']
                phenology_in_location = new_phenology_data[new_phenology_data['지점'] == location]
                for x in range(3):
                    if x == 0:
                        plant_data_x = phenology_in_location[f'{plant}'].to_string().split()
                        plant_data[x] = list(filter(lambda x: len(x) > 7, plant_data_x))
                    else:
                        plant_data_x = phenology_in_location[f'{plant}.{x * 2}'].to_string().split()
                        plant_data[x] = list(filter(lambda x: len(x) > 7, plant_data_x))

                result = ['', '', '']
                period = ['', '', '']
                
                for x in range(3):
                    dates = pd.to_datetime(plant_data[x], errors='coerce')
                    days_of_year = (dates - pd.to_datetime(dates.year, format = '%Y')) / pd.Timedelta(days = 1)
                    result[x] = dict(zip(plant_data[x], days_of_year))
                    period[x] = len(result[x])
                period = max(period)
                
                plant_phenology_df = pd.DataFrame(columns= ['location', 'bud_burst_date', 'bud_burst_days',
                                                            'flowering_date', 'flowering_days', 'fullbloom_date', 'fullbloom_days'])
                plant_phenology_df['location'] = [stn_id['name_en']] * period
                
                for i in range(3):
                    column_name_date = ['bud_burst_date', 'flowering_date', 'fullbloom_date'][i]
                    column_name_days = ['bud_burst_days', 'flowering_days', 'fullbloom_days'][i]
                    plant_phenology_df.loc[:len(result[i]) -1, column_name_date] = list(result[i].keys())
                    plant_phenology_df.loc[:len(result[i])-1, column_name_days] = list(result[i].values())
                
                phenology_df[index] = plant_phenology_df
            
            processed_new_phenology_data = pd.concat(phenology_df)
            
            date_columns = ['bud_burst_date', 'flowering_date', 'fullbloom_date']
            processed_new_phenology_data[date_columns] = processed_new_phenology_data[date_columns].apply(
                pd.to_datetime, errors='coerce')
            processed_new_phenology_data = processed_new_phenology_data.sort_values(
                by=['location'] + date_columns)
            
            if new == True:
                processed_new_phenology_data.to_csv(f'new_{plant_dict[plant]}_phenology_data.csv', index=False, encoding = 'utf-8')
            else:
                processed_new_phenology_data.to_csv(f'{plant_dict[plant]}_phenology_data.csv', index = False, encoding = 'utf-8')
            print(f'Data for {plant_dict[plant]} has been created successfully.')
        print('All Data has been created successfully.')

    def merge_phenology_data(plant_dict, directory = "_phenology_data.csv"):
        plant_list = list(plant_dict.keys())
        
        for plant in plant_list:
            old_file = f"{plant_dict[plant]}{directory}"
            new_file = f"new_{plant_dict[plant]}{directory}"
            old_data = pd.read_csv(old_file, encoding='utf-8')
            new_data = pd.read_csv(new_file, encoding='utf-8')
            
            date_columns = ['bud_burst_date', 'flowering_date', 'fullbloom_date']
            for column in date_columns:
                old_data[column] = pd.to_datetime(old_data[column], errors='coerce')
                new_data[column] = pd.to_datetime(new_data[column], errors='coerce')
            
            merged_data = pd.concat([old_data, new_data]).drop_duplicates(subset=['location'] + date_columns, keep='first')
            merged_data = merged_data.sort_values(by=['location'] + date_columns)
            
            merged_data.to_csv(f"{plant_dict[plant]}{directory}", index=False, encoding='utf-8')
            print(f"Merged data for {plant_dict[plant]} has been saved to original data")
