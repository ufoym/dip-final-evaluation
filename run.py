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
            arr = np.loadtxt(os.path.join(dir_results, fn))

            precisions = []
            for i in xrange(1000):
                truth = i / 100
                truth_num = 0
                total_precision = 0
                for j in xrange(1000):
                    if arr[i, j] == truth:
                        truth_num += 1
                        total_precision += truth_num / float(j+1)
                precisions.append(total_precision / float(truth_num))

            arrs[name] = precisions

    with open(fn_dump, 'wb') as f:
        pickle.dump(arrs, f)

prepare(fn_dump)
with open(fn_dump, 'rb') as f:
    arrs = pickle.load(f)
    # for name, precisions in arrs.iteritems():
    #     print name, precisions[1]


def output_line(fn_html = 'var/result.html', start = 5, num_cases = 50):
    names = arrs.keys()

    # write to html
    with open(fn_html, 'w') as f:
        f.write( "<html><head>\n" )
        f.write( "<meta http-equiv=Content-Type content='text/html;charset=utf-8'>" )
        f.write( "<link rel='stylesheet' href='morris.min.css'>\n" )
        f.write( "<script src='jquery.min.js'></script>\n" )
        f.write( "<script src='raphael-min.js'></script>\n" )
        f.write( "<script src='morris.min.js'></script>\n" )
        f.write( "</head><body>\n" )
        f.write( "<div id='graph' style='text-align:center; height: 360px;'></div>\n" )
        f.write( "<script type='text/javascript'>\n" )
        f.write( "Morris.Line({\n" )
        f.write( "  element: 'graph',\n" )
        f.write( "  parseTime: false,\n" )
        f.write( "  data: [\n" )
        for i in xrange(start, start+num_cases):
            f.write( "    { query: '%d.png'" % i )
            for j, name in enumerate(names):
                f.write( ", ap%d: %2.3f" % (j, arrs[name][i]) )
            f.write( " },\n" )
        f.write( "  ],\n" )
        f.write( "  xkey: 'query',\n" )
        f.write( "  ykeys: ['ap" + "', 'ap".join([str(x) for x in xrange(len(names))]) + "'],\n" )
        f.write( "  labels: ['" + "', '".join([name.encode('utf-8') for name in names]) + "']\n" )
        f.write( "}).on('click', function(i, row){\nconsole.log(i, row);\n});\n" )
        f.write("</script></body><html>")

def output_bar(start, end, fn_html):

    # write to html
    with open(fn_html, 'w') as f:
        f.write( "<html><head>\n" )
        f.write( "<meta http-equiv=Content-Type content='text/html;charset=utf-8'>" )
        f.write( "<link rel='stylesheet' href='style.css'>\n" )
        f.write( "<script src='jquery.min.js'></script>\n" )
        f.write( "<script src='raphael-min.js'></script>\n" )
        f.write( "<script src='morris.min.js'></script>\n" )
        f.write( "</head><body>\n" )

        f.write( "<table style='margin:0 auto;'>\n" )
        for target in xrange(start, end):
            infos = []
            for name in arrs.keys():
                infos.append((name.encode('utf-8'), arrs[name][target]))
            infos.sort(key=lambda x: x[1])

            f.write( "<tr>\n" )
            f.write( "<td style='text-align:right'><img src='images/%d.jpg' width='360px'></img></td>\n" % target )
            f.write( "<td><div id='graph%d' style='height: 300px'></div></td>\n" % target )
            f.write( "</tr>\n" )
        f.write( "</table>\n" )

        for target in xrange(start, end):
            infos = []
            for name in arrs.keys():
                infos.append((name.encode('utf-8'), arrs[name][target]))
            infos.sort(key=lambda x: x[1])

            f.write( "<script type='text/javascript'>\n" )
            f.write( "Morris.Bar({\n" )
            f.write( "  element: 'graph%d',\n" % target )
            f.write( "  parseTime: false,\n" )
            f.write( "  data: [\n" )
            for name, ap in infos[::-1]:
                f.write( "    { group: '%s', ap: '%2.3f' },\n" % (name, ap) )
            f.write( "  ],\n" )
            f.write( "  xkey: 'group',axes:false,\n" )
            f.write( "  ykeys: ['ap'],\n" )
            f.write( "  hideHover: 'auto',\n" )
            f.write( "  labels: ['mAP - %d.png'],\n" % target )
            f.write( "});\n" )
            f.write("</script>")

        f.write("</body><html>")

for i in xrange(0, 1000, 100):
    output_bar(i, i+100, 'var/%d.html' % i)