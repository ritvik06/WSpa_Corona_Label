import pandas as pd
import numpy as np
import sys

df_residents = pd.read_excel('../Data/1609154 Resident updated List of The World Spa Jan -2020 (2).xlsx')
df_visitors = pd.read_csv('../Data/Wspa Visitor 1406-2106.csv')
df_service = pd.read_csv('../Data/Wspa service staff.csv')
df_complaints = pd.read_csv('../Data/Complaints.csv')

#Storing Occupied Households info in a list

#list comprises of 'Tower', 'Apt Num', Names...., Ages...., external entitites tba later

res_info = []

for i in range(len(df_residents)):
    if ((df_residents.iloc[i,2]=='Y' or df_residents.iloc[i,2]=='T') and (df_residents.iloc[i,0]!='SW' or df_residents.iloc[i,0]!='SE')):  
        list_house = []
        list_house.append(df_residents.iloc[i,0])
        list_house.append(df_residents.iloc[i,1])
        # Append Names of residents
        for j in range(int(df_residents.iloc[i,5])):  #Total members in the house
            list_house.append(df_residents.iloc[i,6+(4*j)])
        #Append ages of all residents   
        for j in range(int(df_residents.iloc[i,5])):  
            list_house.append(df_residents.iloc[i,7+(4*j)])
        
#         list_house.append(df_residents.iloc[i,-1])
            
        res_info.append(list_house)

#Randomising covid data for houses with probabilistic randomisation
# res_positive = np.random.choice([0, 1], p=[1.-float(sys.argv[1]), float(sys.argv[1])], size=len(res_info))
res_positive = np.zeros(())

num_povhouses = input("Please input number of houses with positive COVID-19 cases currently : ")



# print("\nNumber of houses with positive COVID-19 cases are %d\n"% len(np.where(res_positive==1)[0]) )

alpha = np.where(res_positive==1)[0]

#Construct fully connected graph for all households
#Node number is index of household in res_info

#Point system depicting points issued by index household to the other houses
#100 points for +ve case in the house, 50 points for immediate neighbours, 10 points per household in tower, 10 points for elderly in house

inter_points = np.zeros((len(res_info), len(res_info)))

for i in range(len(res_info)):
    if (res_positive[i]):
        #identify same towers
        indices = [j for j in range(len(res_info)) if res_info[j][0]==res_info[i][0]]    
        inter_points[i][indices] = 10
        
        #Assign 100 points to the affected house
        inter_points[i][i] = 100
        
        #Assign 50 points to immediate neighbour
        neg = [j for j in indices if np.absolute(res_info[j][1]-res_info[i][1])==1.]
        inter_points[i][neg] = 50
        
    else:
        ages = np.asarray(res_info[i][int((len(res_info[i])/2)+1):-1])
        ages = ages[~np.isnan(ages)]
        
        if (len(np.where(ages>60.))):
            inter_points[i][i] = 10

#Accumulated points by each household
res_points = np.sum(inter_points, axis=0)

#Limit points to 100
res_points = np.clip(res_points,a_min=0,a_max=100.)

# print(res_points)

service_dict = {}

for i in range(len(df_service)):
    if (df_service.iloc[i][3] not in service_dict.keys()):
        service_dict[df_service.iloc[i][3]] = []
        
    house_no = df_service.iloc[i,0].strip().split(' - ')
    try:
        service_dict[df_service.iloc[i][3]].append(house_no[0])
        service_dict[df_service.iloc[i][3]].append(float(house_no[1]))   
    except ValueError:
        #Some random thing
        1+2

#Randomise servicemen having 
service_positive = np.random.choice([0, 1], p=[1. - float(sys.argv[2]), float(sys.argv[2])], size=len(service_dict))

count = 0

for key in service_dict.keys():
    service_dict[key].append(service_positive[count])
    count += 1
    # print(service_dict[key])

#Add 50 points to other houses if servicemen test positive
#Add 50 points to houses if cases is positive in atleast one house and servicemen are common
#Add 20 points to houses if serviceman went to house with points>50

for key in service_dict.keys():
    
    rmax = (len(service_dict[key])//2)  

    if (len(service_dict[key])%2):
        rmax-=1
    
    #If serviceman tested positive
    if(service_dict[key][-1]):
        for i in range(rmax):
            for j in range(len(res_info)):
                if(service_dict[key][2*i]==res_info[j][0] and service_dict[key][2*i+1]==res_info[j][1]):
                    res_points[j]+=50
                    # print(key)  
    
    else:
        for i in range(rmax):
            change = 0
            for j in range(len(res_info)):
                if(service_dict[key][2*i]==res_info[j][0] and service_dict[key][2*i+1]==res_info[j][1]):
                    #If serviceman went to a high risk house, increase points for all houses he went to by 50
                    if(res_positive[j]):
                        change=50
                        break
                    #If serviceman went to a semi high risk house, increase points for all houses he went to by 20
                    elif(res_points[j]<=100 and res_points[j]>=50):
                        change= ((res_points[j]-50)//2)
                    
            for j in range(len(res_info)):
                if(service_dict[key][2*i]==res_info[j][0] and service_dict[key][2*i+1]==res_info[j][1]):
                    res_points[j]+=change

#Limit points to 100
res_points = np.clip(res_points,a_min=0,a_max=100.)

#Houses = 100 are containment zones, colour coded purple
#Houses above 50 are red
#Houses >=20 are yellow
#Rest are green

labels = []
pcount =0 
rcount =0
ycount =0
gcount =0

for i in range(len(res_points)):
    if(res_points[i]==100):
        labels.append('Purple')
        pcount+=1
    elif(res_points[i]<100 and res_points[i]>=50):
        labels.append('Red')
        rcount+=1
    elif(res_points[i]<50 and res_points[i]>=20):
        labels.append('Yellow')
        ycount+=1
    else:
        labels.append('Green')
        gcount+=1

print("Number of containtment zone houses are %d\n"% pcount)
print("Number of Red zone houses are %d\n"% rcount)
print("Number of Yellow zone houses are %d\n"% ycount)
print("Number of Green zone houses are %d\n"% gcount)

tower = input("Enter Your tower : ")

tower_count = 0
tower_pos = []

for i in range(len(res_info)):
    if(tower==res_info[i][0]):
        if(res_positive[i]):  
            tower_pos.append(i)
            tower_count+=1

print("\nNumber of cases in your tower are %d\n"% tower_count)

for i in range(len(tower_pos)):
    print(str(res_info[tower_pos[i]][0]) + "-" + str(int(res_info[tower_pos[i]][1])) + '\n')

house = float(input("Enter your house number : "))

for i in range(len(res_info)):
    if(tower==res_info[i][0] and house==res_info[i][1]):
        print("\nYou are in " + labels[i] + " Zone\n")

        if(labels[i]=="Green"):
            print("You are safe\n")

        elif(labels[i]=="Yellow"):
            print("Caution : Please do not go out unless absolutely necessary\n")

        elif(labels[i]=="Red"):
            print("You are in a high risk zone, please stay inside your household and contact the helpline number in the case of any symptoms\n")

        else:    
            print("You are in a containment zone, you are not allowed to step outside your house. Please contact the helpline number in the case of any symptoms\n")


for i in range(len(res_info)):
    if (res_positive[i]):

        if (tower==res_info[i][0] and house!=res_info[i][1]):
            print("10 points contributed by " + str(res_info[i][0]) + "-" + str(res_info[i][1]) + "/n")


        inter_points[i][indices] = 10
        
        #Assign 100 points to the affected house
        inter_points[i][i] = 100
        
        #Assign 50 points to immediate neighbour
        neg = [j for j in indices if np.absolute(res_info[j][1]-res_info[i][1])==1.]
        inter_points[i][neg] = 50
        
    else:
        ages = np.asarray(res_info[i][int((len(res_info[i])/2)+1):-1])
        ages = ages[~np.isnan(ages)]
        
        if (len(np.where(ages>60.))):
            inter_points[i][i] = 10
