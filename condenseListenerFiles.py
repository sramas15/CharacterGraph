#!/usr/bin/python

in_f = 'listener_predictions/listener-word-triples2.out'
out_f = 'listener_predictions/listener-word-triples2-condensed.out'

with open(in_f) as infile:
    with open(out_f, 'w') as outfile:
        for line in infile:
            words = line.split()
            if len(words) > 0:
                if words[0] == 'Play:':
                    outfile.write('\n' + line)
                elif words[0] == 'avg':
                    outfile.write(words[5] + ' ')
