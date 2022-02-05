
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 18 09:51:20 2022

@author: rodra04
"""

# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 14:15:33 2022

@author: rodra04
"""
#Important libraries import
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import json
import random
import numpy as np
import matplotlib.pyplot as plt
import DataGetter_improved_working
from phone_iso3166.country import *
import pycountry

#Class of the genetic algorithm
class GA():
    
    #Definition and storage of important parameters using to train the algorithm
    def __init__(self, ranges, population_size, data, budget, maxWind, maxSolar, maxWave): 
        
        self.ranges = ranges
        self.population_size = population_size
        self.data = data
        self.budget = budget
        self.maxWave = maxWave
        self.maxSolar = maxSolar
        self.maxWind = maxWind
        
        self.population = []
        
        for i in range(population_size):
            
            x = random.randint(0, ranges[0])
            y = random.randint(0, ranges[1])
            z = random.randint(0, ranges[2])
            
            self.population.append([x, y, z])
        
        
    #Our fitness function
    def fitness_function(self, population):
        
        self.fitness_values = []
        self.prices = []
        
       # print(self.data[2][2])
        for individual in population:
            
            #Bring score of individuals that pass the budget or if the maximums are passed
            if individual[0] > self.maxWind or individual[1] > self.maxSolar or individual[2] > self.maxWave or individual[0]*self.data[0][0] +  individual[1]*self.data[1][0] + individual[2]*self.data[2][0] > self.budget:
                penalty_check = True
            else:
                penalty_check = False
            
            if penalty_check == True:
                
                fitness_individual_value = 0
            #Fitness score of individuals
            else:
                
                fitness_individual_value = individual[0]*self.data[0][1] +  individual[1]*self.data[1][1] + individual[2]*self.data[2][1]
                
                if fitness_individual_value < 0:
                    fitness_individual_value = -(fitness_individual_value)
            self.fitness_values.append(fitness_individual_value)
            self.prices.append(individual[0]*self.data[0][0] +  individual[1]*self.data[1][0] + individual[2]*self.data[2][0])
            
        self.fitness_values_array = np.array(self.fitness_values)
        
    
        return self.fitness_values_array, self.prices
    
    #Selection Function
    def selection(self, population, fitness_values_array):
        
        self.individuals_selected = []
        
        for i in fitness_values_array:
            self.individuals_selected.append(i/max(fitness_values_array))
        
        #print(self.individuals_selected)
        self.reproduce = []
        #The probability of reproduction is the normalized fitness value (between 0 and 1)
        individual = 0
        while len(self.reproduce) <= 100:
           
            if individual == len(population):
                break
            number = random.randint(1, 100)
            
            if number <= self.individuals_selected[individual]*100:
                
                self.reproduce.append(population[individual])
            
            individual += 1
            
            
        
        return self.reproduce
    
    #Crossover of parens
    def combination(self, reproduce):
        
        self.children = []
        
        count = 0
        
        for pairs in range(len(reproduce)-1):
            
            cutoff = random.randint(1, 2)
           # print("cut off is", cutoff)
            first_parent = reproduce[pairs]
            second_parent = reproduce[pairs + 1]
            count += 1
            
            first_to_second = []
            second_to_first = []
            
            for genes in range(cutoff):
                
                first_parent_chromosome = first_parent[genes]
                second_parent_chromosome = second_parent[genes]
                
                first_to_second.append(first_parent_chromosome)
                second_to_first.append(second_parent_chromosome)
           # print(first_to_second, second_to_first)
            
            for change in range(cutoff):
                
                first_parent[change] = second_to_first[change]
                second_parent[change] = first_to_second[change]
        
            self.children.append(first_parent)
            self.children.append(second_parent)
        
        return self.children
    
    #Mutation function
    def mutation(self, children, fitness, mutation_matrix, probability):
        
        
        self.mutated_children = []
        
        for individual in children:
            
            #If mutate, use the mutation matrix to modify a random gene of the individual 
            if random.randint(0, 100) <= probability:
                
                modified = [0, 0, 0]
                random_chromosome = random.randint(0, 2)
                #print(random_chromosome)
                mutation_action = random.random()
                
                if mutation_action <= mutation_matrix[random_chromosome][0]:
                    #print("sum")
                    modified[random_chromosome] = individual[random_chromosome] + 1
                    action = 0
                    counteraction = 1
                elif mutation_action > mutation_matrix[random_chromosome][0] and (individual[random_chromosome] - 1) > 0:
                    #print("sub")
                    modified[random_chromosome] = individual[random_chromosome] - 1
                    action = 1
                    counteraction = 0
                else:
                    action = 1
                    counteraction = 0
                    modified[random_chromosome] = individual[random_chromosome] + 0
                    
                for i in range(len(modified)):
                    if i != random_chromosome:
                        modified[i] = individual[i]
                
                for gene in range(len(modified)):
                    if modified[gene] > self.ranges[gene]:
                        ilegal = True
                        
                    else:
                        ilegal = False
                if ilegal == False:       
                
                    score_of_mutation, price = self.fitness_function([individual, modified])
                if ilegal == True:
                    score_of_mutation = [100, 0]
                #print(score_of_mutation)
                
                if score_of_mutation[0] > score_of_mutation[1]:
                    #print("Success")
                    mutation_matrix[random_chromosome][counteraction] += (score_of_mutation[0]-score_of_mutation[1])/score_of_mutation[0]
                    mutation_matrix[random_chromosome][action] -= (score_of_mutation[0]-score_of_mutation[1])/score_of_mutation[0]
                
                elif score_of_mutation[0] < score_of_mutation[1]:
                    #print("Fail")
                    
                    mutation_matrix[random_chromosome][counteraction] -= (score_of_mutation[1]-score_of_mutation[0])/score_of_mutation[0]
                    mutation_matrix[random_chromosome][action] += (score_of_mutation[1]-score_of_mutation[0])/score_of_mutation[0]
                    
                #print(mutation_matrix)
                self.mutated_children.append(modified)
                #print(mutation_matrix)
            
            else:
                self.mutated_children.append(individual)
       
        #print(self.best, max(self.fitness_values))
        
        
        return self.mutated_children, mutation_matrix



#HTTP Server to interact with algorithm
app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

country = ""
budget_money = 248000000
region_list = []

@app.route('/data', methods = ['POST'])
@cross_origin()
def getdata():
    global country
    global budget_money
    global region_list
    country = pycountry.countries.get(alpha_2 = phone_country(int(json.loads(request.data)["country"][1:]))).name
    regions = DataGetter_improved_working.solarOutput(country, 'other', None)
    
    for i in regions:
        region_list.append([i])
    
    return jsonify(budget_money, country, regions)
print(region_list, country)
@app.route('/region', methods = ['GET'])
@cross_origin()
def getregion():
    global region_list
    print(region_list)
    response = region_list
    
    return jsonify(response)

@app.route('/selected', methods = ['POST'])
@cross_origin()
def postregion():
    global region
    global country
    region = json.loads(request.data)["region"]
    print(region)
    return jsonify(region, country)

@app.route('/train', methods = ['GET'])
@cross_origin()

#Training process
def train():
    global country
    global budget_money
    global region
    data = [DataGetter_improved_working.windOutput(DataGetter_improved_working.get_weather(country, 'other')), DataGetter_improved_working.solarOutput(country, 'kilowatts', region), DataGetter_improved_working.waveOutput(country)]


    if data[2][1] == 0:
        wind = 50000000000
        solar = 5000000000000
        wave = 0
    else:
        wind = 100000000000000 
        solar = 1000000000000 
        wave = 1000000000000

    redlight = True
    errorOccured = False
    
    #Training loop
    while redlight:
        try:
            algo = GA(ranges = [wind, solar, wave], population_size = 10000, data = data, budget = budget_money, maxWind = 10000, maxSolar = 10000, maxWave = 1000)   
            
            initial_pop = algo.population
            matrix = [[0.5, 0.5], [0.5, 0.5], [0.5, 0.5]]
            generation = []
            best_values = []
            prices_of_thebest = []
            probability = 100
            probability_min = 2
            
            i = 1
            
            
            for initialize in range(500):
                fitness, price = algo.fitness_function(initial_pop)
                
                selected= algo.selection(initial_pop, fitness)
                
                children = algo.combination(selected)
               
                new_pop, matrix = algo.mutation(children, fitness, matrix, probability)
                initial_pop = new_pop
                probability -= 1/(i/10)
                if probability < probability_min:
                    probability = probability_min
                
                if len(initial_pop) != 0:
                    best_values.append(max(fitness))
                    generation.append(i)
                    prices_of_thebest.append(price[list(fitness).index(max(fitness))])
                i += 1
            count = 0       
            best_children = []
            
            
            
            
            
            while best_values[len(best_values)-1] != best_values[len(best_values)-199] and budget_money - max(prices_of_thebest) > 10000 and count < 10000:
                fitness, price = algo.fitness_function(initial_pop)
                selected= algo.selection(initial_pop, fitness)
                
                children = algo.combination(selected)
                new_pop, matrix = algo.mutation(children, fitness, matrix, probability)
                
                initial_pop = new_pop
                probability += 1/(i/70)
                if probability > probability_min:
                    probability = probability_min
                
                if len(initial_pop) != 0:
                    best_values.append(max(fitness))
                    generation.append(i)
                    best_children.append(initial_pop[list(fitness).index(max(fitness))])
                    prices_of_thebest.append(price[list(fitness).index(max(fitness))])
                i += 1
                count += 1
            
            redlight = False
            
        except IndexError:
            wind = int(wind / 10)
            solar = int(solar / 10)
            if wave != 0:
                wave = int(wave / 10)
    print([best_children[len(best_children)-1], best_values[len(best_values)-1], prices_of_thebest[len(prices_of_thebest)-1]])
    return jsonify([best_children[len(best_children)-1], round(best_values[len(best_values)-1], 2), prices_of_thebest[len(prices_of_thebest)-1]])
   
          
app.run(host = "0.0.0.0", port = 5000)
