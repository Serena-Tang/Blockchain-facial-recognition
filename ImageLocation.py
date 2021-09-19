# -*- coding: utf-8 -*-
import exifread, requests, os, optparse


class ImageLocation:
    def __init__(self, img_dir='', img=''):
        self.img_dir, self.img = img_dir, img
        # picked a random ak
        self.ak = 'YiSITcGEkm7z6ITj54gKVQbuTiQno7u8'

    def run(self):
        return self.dir_file() if self.img_dir else [self.exifread_infos(self.img)]

    # Iterate through image catalogs, non-recursive traversal to get an array of image information
    def dir_file(self):
        files = [os.path.join(self.img_dir, i) for i in os.listdir(self.img_dir) if not os.path.isdir(i)]
        infos = [self.exifread_infos(img) for img in files]
        return infos

    # Get photo time, device, latitude and longitude information
    # photo parameter: photo file path
    def exifread_infos(self, photo):
        if not os.path.exists(photo):
            return {}
        f = open(photo, 'rb')
        tags = exifread.process_file(f)

        try:
            # Time
            time = tags["EXIF DateTimeOriginal"].printable
            # Latitude
            LonRef = tags["GPS GPSLongitudeRef"].printable
            Lon = tags["GPS GPSLongitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
            Lon = float(Lon[0]) + float(Lon[1]) / 60 + float(Lon[2]) / float(Lon[3]) / 3600
            if LonRef != "E":
                Lon = Lon * (-1)    
            # Longitude
            LatRef = tags["GPS GPSLatitudeRef"].printable
            Lat = tags["GPS GPSLatitude"].printable[1:-1].replace(" ", "").replace("/", ",").split(",")
            Lat = float(Lat[0]) + float(Lat[1]) / 60 + float(Lat[2]) / float(Lat[3]) / 3600
            if LatRef != "N":
                Lat = Lat * (-1)    
            # Device
            device = tags["Image Make"].printable + tags["Image Model"].printable
            f.close()
            # Address
            addr = self.get_location(Lon, Lat)
            return {'photo': photo, 'lon': Lon, 'lat': Lat, 'time': time, 'device': device, 'addr': addr}
        except:
            return {}

    # Fetch Address According to Latitude and Longitude
    def get_location(self, lon, lat):
        items = {'location': str(lat) + "," + str(lon), 'ak': self.ak, 'output': 'json'}
        header = {'Referer': '1.grayddq.top'}
        res = requests.get('http://api.map.baidu.com/geocoder/v2/', params=items, headers=header).json()
        return res['result']['formatted_address'] if res['status'] == 0 else ""


if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option("-d", "--dir", dest="dir", help=u"target dir，demo: -d /home/root/")
    parser.add_option("-p", "--img", dest="img", help=u"target photo，demo: -p 1.jpg")
    options, _ = parser.parse_args()
    if options.dir or options.img:
        infos = ImageLocation(img_dir=options.dir).run() if options.dir else ImageLocation(img=options.img).run()
        for info in infos:
            if len(info)>0:
                print (u"Image：%s\n Device：%s\n Time：%s\n Address：%s\n Latitude：%s\n Longitude：%s\n******************" % (
                    info['photo'], info['device'], info['time'], info['addr'], info['lon'], info['lat']))
    else:
        parser.print_help()
