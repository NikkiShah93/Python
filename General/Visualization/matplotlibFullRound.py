## In this script we will go through the matplotlib library
## and explore different functionalities that can come in handy

## first the imports
import matplotlib.pyplot as plt
import numpy as np

## we will use numpy for generating data
x = np.linspace(-5, 5, 100)
y = np.sin(x)/(2 * np.pi) 

## the first/simple type of plot would be scatter
# plt.scatter(x, y, color = 'green', marker = '*', s = 50, alpha=0.5)
# plt.show()

## now lets generate an example for line plot
years = np.arange(2000, 2025, 1)
price = (np.sin(years/2)*np.cos(years)/2*np.pi) * 10000 + 500

## the default plot is a line plot 
# plt.plot(years, price, color='green', lw = 2, linestyle='--')
## we can accomplish the same in less code
# plt.plot(years, price, 'g--', lw = 2)
# plt.show()

## now moving to categorical data
lang = np.array(['C++', 'C#', 'Java','Python','Go', 'Ruby'])
vals = np.random.randint(low=0, high=50, size = len(lang)) * 2

# plt.bar(lang, vals, color ='green', width=0.5, edgecolor = 'red', lw=1)
# plt.show()

## and histograms can be helful to show distributions
ages = np.random.normal(30, 3, 1000)

# plt.hist(ages, bins=20, cumulative=True)
# plt.show()

## moving to pie chart could be helpful
## when we have independent categories
## using the lang and vals example again
## we can also explode one of the pieces 
## we can use pctdistance to move the % outside
## but didn't find it that appealing
explode = [0.2 if x == 'Python' else 0 for x in lang]
plt.pie(x=vals, labels=lang,normalize=True, explode=explode,
        autopct='%.1f%%', startangle=90)
plt.show()
