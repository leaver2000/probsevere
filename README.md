# NOAA/CIMSS ProbSevere 

ProbSevere is a rapidly updating real-time system, which integrates remotely sensed observations of thunderstorms and mesoscale NWP, producing short-term probabilistic guidance of future severity. Specifically, ProbSevere predicts the probabilities of severe hail, severe wind, tornado, or any severe weather in the next 60 minutes for every storm over the CONUS.

This python module attemps to extend the ProbSevere model by applying various storm motion vectors.


![image](https://user-images.githubusercontent.com/76945789/135806503-02ba51bd-9af2-499a-81b1-9089104fe9a1.png)


![image](https://user-images.githubusercontent.com/76945789/135806799-35f2f394-6e1c-4561-bedc-11a1171b23bc.png)


PSv3 uses a new machine-learning model, and incorporates SPC mesoanalysis, GOES-16 GLM, additional GOES-16 ABI data, and additional MRMS data.
Spatial patterns in 0.64-µm ref., 10.3-µm BT, and GLM flash-extent density are incorporated

PSv3 is more skillful and better-calibrated than PSv2.
The best probability thresholds (i.e., where CSI is maximized) are lower for PSv3 (~40-60%) vs. PSv2 (~60-80%).
Forecasters will notice threatening storms have lower probabilities in v3, compared to v2. 

It may be more difficult to determine what caused a change in the probability.
We are working on display methods for better interpretability for users.

## ProbSevere v3 models

The four models are gradient-boosted decision-tree classifiers

inpust sourcesL MRMS, ENTLN, GOES-East and SPC mesoanalysis


![image](https://user-images.githubusercontent.com/76945789/135807413-ab4a1e03-4b70-4889-aef2-3a77e5287d05.png),![image](https://user-images.githubusercontent.com/76945789/135807429-9da75b62-5a7d-4de5-9ba5-8d27011b0a91.png)

![image](https://user-images.githubusercontent.com/76945789/135807446-aea541f4-7c88-4cc7-8d2a-cb4708410603.png),![image](https://user-images.githubusercontent.com/76945789/135807455-ea2d5bef-b200-43b6-b5f9-b7870c925605.png)


https://cimss.ssec.wisc.edu/satellite-blog/archives/34480

https://journals.ametsoc.org/view/journals/wefo/aop/WAF-D-20-0028.1/WAF-D-20-0028.1.xml



## PSv3 improvement over PSv2


![image](https://user-images.githubusercontent.com/76945789/135807720-978cf8aa-93a0-4061-90a9-730785404d1d.png)





```python
stm=storm[691240]
latrange=[38,39.5]
lonrange=[-80.5,-78]

lon_0 = np.mean(lonrange)
lat_0 = np.mean(latrange)
m = Basemap(projection='merc',lon_0=lon_0, lat_0=lat_0, lat_ts=lat_0,
            llcrnrlat=np.min(latrange), urcrnrlat=np.max(latrange),
            llcrnrlon=np.min(lonrange), urcrnrlon=np.max(lonrange))


# m.drawcoastlines()
# m.drawmapboundary(fill_color='#46bcec')
# m.fillcontinents(color = 'white',lake_color='#46bcec')

crds = stm['coordinates'][0]
print(crds)
lon0,lat0=np.rollaxis(np.array(crds), 2, 0)
x0,y0=m(lon0,lat0)
m.plot(*x0,*y0, marker=None,color='b')



stm_trk = stm['st_linear'][0]


lons, lats = np.rollaxis(np.array([stm_trk]), 2, 0)

x,y=m(lons,lats)

m.plot(x,y,marker="D",color='m')
plt.show()

```



``` python

def scale_map(x):
    llclat=lats.min()-x
    urclat=lats.max()+x
    urclon=lons.min()-x
    llclon=lons.max()+x
    return Basemap(projection='merc',llcrnrlat=llclat,urcrnrlat=urclat,
                   llcrnrlon=urclon,urcrnrlon=llclon,lat_ts=20,resolution='c') 


plt.figure(dpi=150)

m = scale_map(.5)
x,y = m(*lons,*lats) 
m.plot(x, y, marker=None,color='m')

_x,_y = m(*centroid) 
m.plot(_x, _y, marker='D',color='b')

m.drawcoastlines() 
m.drawmapboundary()


plt.show()



stm=storm[691240]
latrange=[20,55]
lonrange=[-140,-60]

lon_0 = np.mean(lonrange)
lat_0 = np.mean(latrange)
m = Basemap(projection='merc',lon_0=lon_0, lat_0=lat_0, lat_ts=lat_0,
            llcrnrlat=np.min(latrange), urcrnrlat=np.max(latrange),
            llcrnrlon=np.min(lonrange), urcrnrlon=np.max(lonrange))


m.drawcoastlines()
# parallels = np.arange(0.,81,10.)
# m.drawparallels(parallels,labels=[False,True,True,False])
# m.drawmeridians(meridians,labels=[True,False,False,True])
m.drawmapboundary(fill_color='#46bcec')
m.fillcontinents(color = 'white',lake_color='#46bcec')
# x,y=m(-70,30)
# m.plot(x,y, marker='D',color='m')
plt.show()
# print(stm['st_linear'],stm['slopes'])
for i, pol in enumerate(stm['st_linear']):

#     x,y = stm["slopes"][i]
#     print(f'slope={y/x}')
#     print(f'lineartrack={pol[0]}\n')
#     plt.plot(*pol,'x')
    
    a,b,c,d,e =pol
#     x1,y1=
    x2,y2=m(b[0],b[1])
    m.plot(x2,y2, marker='D',color='m')
    
    
    
    print(a)
   
#     plt(*pol[0])
#     print(stm['coordinates'][i])





```
