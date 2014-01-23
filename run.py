# -*- coding: utf-8 -*-
import os
import numpy as np
import cPickle as pickle

fn_dump = 'var/result.dump'
dir_results = 'var/results/'

def prepare(fn_dump):
    arrs = {}
    for fn in os.listdir(dir_results):
        if fn.endswith('.txt'):
            fn = fn.decode('gbk')
            name = ' '.join(fn[:-4].split('_'))
            print name
            arr = np.loadtxt(os.path.join(dir_results, fn), np.int)

            precisions = []
            for i in xrange(1000):
                truth = i / 100
                truth_num = 0
                total_precision = 0
                for j in xrange(1000):
                    if arr[i, j] / 100 == truth:
                        truth_num += 1
                        total_precision += truth_num / float(j+1)
                precisions.append(total_precision / float(truth_num))

            arrs[name] = precisions

    with open(fn_dump, 'wb') as f:
        pickle.dump(arrs, f)

# prepare(fn_dump)
with open(fn_dump, 'rb') as f:
    arrs = pickle.load(f)

def output_bar(start, num, fn_html):
    nav = []
    for i in xrange(0, 1000, num):
        nav.append('<li%s><a href="%d.html">%d-%d</a></li>' % (' class="active"' if i == start else '', i, i, i+num-1))

    content, script = [], []
    for target in xrange(start, start+num):
        infos = []
        for name in arrs.keys():
            infos.append((name.encode('utf-8'), arrs[name][target]))
        infos.sort(key=lambda x: x[1])

        content.append('''
            <div class="row stat">
              <div class="col-lg-4">
                <h4>%d.jpg</h4>
                <img src='images/%d.jpg' width='100%%'></img>
              </div>
              <div class="col-lg-8">
                <h4></h4>
                <div id='graph%d' style='height: 250px'></div>
              </div>
            </div>
            ''' % (target, target, target) )

        script.append('''
            Morris.Bar({
              element: 'graph%d',
              parseTime: false,
              data: [
                %s
              ],
              xkey: 'group',axes:false,
              ykeys: ['ap'],
              ymin: 0,
              ymax: 1,
              hideHover: 'auto',
              labels: ['mAP - %d.jpg'],
            });
            ''' % ( target,
                    '\n'.join(["{ group: '%s', ap: '%2.3f' }," % (name, ap) for name, ap in infos[::-1]]),
                    target))

    html = '''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="">
        <meta name="author" content="">

        <title>DIP</title>
        <link href="bootstrap.min.css" rel="stylesheet">
        <link href="style.css" rel="stylesheet">
        <!-- HTML5 shim and Respond.js IE8 support of HTML5 elements and media queries -->
        <!--[if lt IE 9]>
          <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
          <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
        <![endif]-->

        <link rel='stylesheet' href='morris.min.css'>
        <script src='jquery.min.js'></script>
        <script src='raphael-min.js'></script>
        <script src='morris.min.js'></script>

      </head>
      <body>
        <div class="container">
          <div class="header">
            <ul class="nav nav-pills pull-right">
                %s
            </ul>
          </div>
          %s
          <div class="footer">
            <p>&copy; DIP 2013</p>
          </div>
        </div>
        <script type="text/javascript">
          %s
        </script>
      </body>
    </html>
    ''' % (''.join(nav), '\n'.join(content), '\n'.join(script))

    with open(fn_html, 'w') as f:
        f.write(html)

for i in xrange(0, 1000, 100):
    output_bar(i, 100, 'var/%d.html' % i)