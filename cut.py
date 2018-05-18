import subprocess, argparse, sys, re

class Time():
    def __init__(self, time):
        if(not re.match('\d{2}:[0-6]\d:[0-6]\d', time)):
            print('Введите время в формате чч:мм:сс')
            exit(1)
        self.str_time = time
        self.seconds = int(time[:2]) * 3600
        self.seconds += int(time[3:5]) * 60
        self.seconds += int(time[6:])

def createParser():
    parser = argparse.ArgumentParser()
    parser.add_argument('name')
    parser.add_argument('time', nargs='+')
    return parser

if __name__ == '__main__':
    parser = createParser()
    namespase = parser.parse_args(sys.argv[1:])

    ls = subprocess.Popen('ls', shell=True, stdout=subprocess.PIPE)
    if re.search(namespase.name, ls.communicate()[0].decode()) == None:
        print('В папке нет файла ' + namespase.name)
        exit(1)

    time_file = Time(re.search(r'(?<=Duration: )\d{2}:[0-6]\d:[0-6]\d',
                               subprocess.Popen('avconv -i ' + namespase.name,
                                                shell=True,
                                                stderr=subprocess.PIPE).communicate()[1].decode()).group())
    format_ = '.' + str(namespase.name).split('.')[1]
    time = []
    for t in namespase.time:
        t_ = Time(t)
        if t_.seconds > time_file.seconds:
            t_ = time_file
        time.append(t_)

    if len(time) % 2 == 1:
        time.append(time_file)

    print('Идет обработка...')

    for i in range(len(time) // 2):
        print('Обработано сегментов: ' + str(i))
        if time[i * 2].seconds > time[i * 2 + 1].seconds:
            t_ = time[i * 2]
            time[i * 2] = time[i * 2 + 1]
            time[i * 2 + 1] = t_
        dir = str(time[i * 2].seconds)
        proc = subprocess.Popen('mkdir ' + dir, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()

        proc = subprocess.Popen('avconv -ss ' + str(time[i * 2].seconds)
                         + ' -t ' + str(time[i * 2 + 1].seconds - 2 * time[i * 2].seconds)
                         + ' -i ' + namespase.name + ' -vcodec copy -acodec copy '
                         + dir + '/' + namespase.name,
                         shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        proc.wait()

