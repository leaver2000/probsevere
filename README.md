# binder
![image](https://user-images.githubusercontent.com/76945789/135806394-5e704ad4-3e5f-4126-be33-6ff0da583ab4.png)

![image](https://user-images.githubusercontent.com/76945789/135806417-2e23e8d0-1d8c-4495-b9bd-c32ecbf7565d.png)

![image](https://user-images.githubusercontent.com/76945789/135806427-562dc038-2ac5-4f61-ad9e-26da777e203e.png)

![image](https://user-images.githubusercontent.com/76945789/135806432-0915fdeb-4e6b-4f1c-a15c-73dc534cfb04.png)

![image](https://user-images.githubusercontent.com/76945789/135806440-604f02a5-603a-404e-b14b-f1b2a1ec39fb.png)

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
