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
price = (np.sin(years/2)*np.cos(years)/2*np.pi) * 1000 + 2500

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
# plt.pie(x=vals, labels=lang,normalize=True, explode=explode,
#         autopct='%.1f%%', startangle=90)
# plt.show()

## the next plot that we will be working with
## is the useful boxplot, great for statistical analysis
## showing the min, max, and the quartiles of the set
heights = np.random.normal(68, 5, 500)

# plt.boxplot(heights,notch=True)
# plt.show()

## now more advanced plots
## we will be using the years data again
## styling the price ticks
price_ticks = list(range(int(price.min()) - 50, int(price.max()) + 50, 500))
price_2 = (np.sin(years/2)*np.cos(years)/np.pi) * 1000 + 2500
price_3 = (np.sin(years/3)*np.cos(years)/np.pi) * 1000 + 2000
plt.plot(years, price, label='California')
plt.plot(years, price_2, label = 'Texas')
plt.plot(years, price_3, label= 'New York')
plt.title('Housing Prices', fontsize = 20, fontname = 'Georgia')
plt.ylabel(r'Average Prices ($ \$k $)')
plt.xlabel('Year')
plt.yticks(price_ticks, [f'${round(x)}k' for x in price_ticks])
plt.legend()
plt.show()

