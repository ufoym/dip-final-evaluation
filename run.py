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



def html_template(nav, title, intro, stat, script):
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
            body {padding-top: 70px;}
            h1,h2,h3,h4,h5,p {font-family: "Microsoft YaHei"}
            .stat_image {margin-bottom: 100px;}
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
              <a class="navbar-brand" href="index.html">所有类别</a>
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
            <p>%s</p>
            <div id='graph' style='height: 300px'></div>
          </div>
          %s
          <div class="footer">
            <p>&copy; DIP课程组 2014</p>
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
    ''' % (nav, title, intro, stat, script)
    return html

def output_subpage(start, num):
    nav = []
    for i in xrange(0, 1000, num):
        nav.append('<li%s><a href="%d.html">类别%d</a></li>' % (
            ' class="active"' if i == start else '', i/100, i/100))

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
          labels: ['类别%d的平均查准率'],
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
                <h4>%d.jpg查准率</h4>
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
              labels: ['%d.jpg的查准率'],
            });
            ''' % ( target,
                    '\n'.join(["{ group: '%s', ap: '%2.3f' }," % (
                        name, ap) for name, ap in infos[::-1]]),
                    target))

    return html_template(
        ''.join(nav),
        u'类别%d平均查准率'.encode('utf-8') % (start / 100),
        u'以下为每个小组查询类别%d的图像（%d.jpg - %d.jpg）的平均查准率。'
        u'<br/>下方为每个小组查询该类别下单张图的查准率。'.encode('utf-8') % (
            start / 100, start, start+num-1),
        '\n'.join(stat),
        '\n'.join(script))



def output_homepage(num):
    nav = []
    for i in xrange(0, 1000, num):
        nav.append('<li><a href="%d.html">类别%d</a></li>' % (i/100, i/100))

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
          labels: ['所有类别平均查准率'],
        });
        ''' % ( '\n'.join(["{ group: '%s', ap: '%2.3f' }," % (
                    name, ap) for name, ap in infos[::-1]])))

    return html_template(
        ''.join(nav),
        u'所有类别平均查准率'.encode('utf-8'),
        u'以下为每个小组查询所有类别的图像（共1000张）的平均查准率（鼠标移在'
        u'直方图上方会显示具体的小组成员和查准率）。注：顶部导航条可查询每一'
        u'类别/每张图的查准率。'.encode('utf-8'),
        '',
        '\n'.join(script))


with open('var/index.html', 'w') as f:
    f.write(output_homepage(100))

for i in xrange(0, 1000, 100):
    with open('var/%d.html' % (i/100), 'w') as f:
        f.write(output_subpage(i, 100))