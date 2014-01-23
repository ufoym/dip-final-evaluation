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



def html_template(nav, title, stat, script):
    html = '''
    <!DOCTYPE html>
    <html>
      <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="">
        <meta name="author" content="">
        <title>DIP Final Project</title>
        <link href="bootstrap.min.css" rel="stylesheet">
        <link rel='stylesheet' href='morris.min.css'>
        <!--[if lt IE 9]>
          <script src="https://oss.maxcdn.com/libs/html5shiv/3.7.0/html5shiv.js"></script>
          <script src="https://oss.maxcdn.com/libs/respond.js/1.3.0/respond.min.js"></script>
        <![endif]-->
        <style type="text/css">
            body {min-height: 2000px; padding-top: 70px;}
            .morris-hover{position:absolute;z-index:1000;}
            .morris-hover.morris-default-style{border-radius:10px;padding:6px;
                color:#666;background:rgba(255, 255, 255, 0.8);
                border:solid 2px rgba(230, 230, 230, 0.8);
                font-family:sans-serif;font-size:12px;text-align:center;}
            .morris-hover.morris-default-style .morris-hover-row-label{font-weight:bold;margin:0.25em 0;}
            .morris-hover.morris-default-style .morris-hover-point{white-space:nowrap;margin:0.1em 0;}
        </style>
      </head>
      <body>
        <div class="navbar navbar-default navbar-fixed-top" role="navigation">
          <div class="container">
            <div class="navbar-header">
              <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-collapse">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
              </button>
              <a class="navbar-brand" href="index.html">DIP Final Project</a>
            </div>
            <div class="navbar-collapse collapse">
              <ul class="nav navbar-nav">
                %s
              </ul>
            </div><!--/.nav-collapse -->
          </div>
        </div>


        <div class="container">
          <div class="jumbotron">
            <h1>%s</h1>
            <div id='graph' style='height: 300px'></div>
          </div>
          %s
          <div class="footer">
            <p>&copy; DIP 2013</p>
          </div>
        </div>

        <script src='jquery.min.js'></script>
        <script src='raphael-min.js'></script>
        <script src='morris.min.js'></script>
        <script type="text/javascript">
          %s
        </script>
      </body>
    </html>
    ''' % (nav, title, stat, script)
    return html

def output_subpage(start, num):
    nav = []
    for i in xrange(0, 1000, num):
        nav.append('<li%s><a href="%d.html">%d-%d</a></li>' % (
            ' class="active"' if i == start else '', i, i, i+num-1))

    stat, script = [], []

    # -------------------------------------------------------------------------
    # class stat

    infos = []
    for name in arrs.keys():
        mAP = 0
        for target in xrange(start, start+num):
            mAP += arrs[name][target]
        mAP /= float(num)

        infos.append((name.encode('utf-8'), mAP))
    infos.sort(key=lambda x: x[1])

    script.append('''
        Morris.Bar({
          element: 'graph',
          parseTime: false,
          data: [
            %s
          ],
          xkey: 'group',axes:false,
          ykeys: ['ap'],
          ymin: 0,
          ymax: 1,
          hideHover: 'auto',
          labels: ['mAP - Class %d'],
        });
        ''' % ( '\n'.join(["{ group: '%s', ap: '%2.3f' }," % (
                    name, ap) for name, ap in infos[::-1]]),
                start / 100))


    # -------------------------------------------------------------------------
    # image stat

    for target in xrange(start, start+num):
        infos = []
        for name in arrs.keys():
            infos.append((name.encode('utf-8'), arrs[name][target]))
        infos.sort(key=lambda x: x[1])

        stat.append('''
            <div class="row stat_image">
              <div class="col-lg-4">
                <h4>%d.jpg</h4>
                <img src='images/%d.jpg' width='100%%'></img>
              </div>
              <div class="col-lg-8">
                <h4></h4>
                <div id='graph%d' style='height: 360px'></div>
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
              labels: ['AP - %d.jpg'],
            });
            ''' % ( target,
                    '\n'.join(["{ group: '%s', ap: '%2.3f' }," % (
                        name, ap) for name, ap in infos[::-1]]),
                    target))

    return html_template(''.join(nav), '%d - %d' % (start, start+num-1),
            '\n'.join(stat), '\n'.join(script))



def output_homepage(num):
    nav = []
    for i in xrange(0, 1000, num):
        nav.append('<li><a href="%d.html">%d-%d</a></li>' % (i, i, i+num-1))

    stat, script = [], []

    # -------------------------------------------------------------------------
    # class stat

    infos = []
    for name in arrs.keys():
        mAP = np.mean(arrs[name])
        infos.append((name.encode('utf-8'), mAP))
    infos.sort(key=lambda x: x[1])

    script.append('''
        Morris.Bar({
          element: 'graph',
          parseTime: false,
          data: [
            %s
          ],
          xkey: 'group',axes:false,
          ykeys: ['ap'],
          ymin: 0,
          ymax: 1,
          hideHover: 'auto',
          labels: ['mAP'],
        });
        ''' % ( '\n'.join(["{ group: '%s', ap: '%2.3f' }," % (
                    name, ap) for name, ap in infos[::-1]])))

    return html_template(''.join(nav), 'mAP', '', '\n'.join(script))


with open('var/index.html', 'w') as f:
    f.write(output_homepage(100))

for i in xrange(0, 1000, 100):
    with open('var/%d.html' % i, 'w') as f:
        f.write(output_subpage(i, 100))