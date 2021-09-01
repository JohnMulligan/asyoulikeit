import re
import os


sweeps = {}

all_plays = {'taming_of_the_shrew': ['86473', '89203'], 'henry_vi_part_1': ['3154', '5866'], 'henry_vi_part_2': ['9300', '12507'], 'henry_vi_part_3': ['12508', '15464'], 'macbeth': ['68034', '70486'], 'hamlet': ['44037', '48203'], 'richard_iii': ['79534', '83298'], 'twelfth_night': ['91514', '94147'], 'merchant_of_venice': ['65298', '68033'], 'king_john': ['50861', '53548'], 'henry_v': ['37376', '40747'], 'a_midsummer_nights_dream': ['63065', '65297'], 'loves_labors_lost': ['53549', '56448'], 'timon_of_athens': ['97530', '100089'], 'henry_viii': ['40748', '44036'], 'coriolanus': ['27792', '31686'], 'alls_well_that_ends_well': ['15465', '18543'], 'troilus_and_cressida': ['105021', '108596'], 'cymbeline': ['31687', '35477'], 'two_gentlemen_of_verona': ['89204', '91513'], 'king_lear': ['56449', '60093'], 'romeo_and_juliet': ['83299', '86472'], 'henry_iv_part_2': ['5867', '9299'], 'antony_and_cleopatra': ['24173', '27791'], 'the_tempest': ['102658', '105020'], 'henry_iv_part_1': ['1', '3153'], 'the_winters_tale': ['108597', '112075'], 'pericles': ['74170', '76671'], 'julius_caesar': ['48204', '50860'], 'as_you_like_it': ['18544', '21405'], 'much_ado_about_nothing': ['21406', '24172'], 'two_noble_kinsmen': ['94148', '97529'], 'richard_ii': ['76672', '79533'], 'the_merry_wives_of_windsor': ['112076', '114985'], 'measure_for_measure': ['60094', '63064'], 'othello': ['70487', '74169'], 'titus_andronicus': ['100090', '102657'], 'the_comedy_of_errors': ['35478', '37375']}

output_files = [i for i in os.listdir('.') if i.endswith('.out')]

for outfile in output_files:
	d = open(outfile)
	t = d.read()
	results_count = re.search("(?<=results_count=)[0-9]+",t).group(0)
	window_size = re.search("(?<=window_size=)[0-9]+",t).group(0)
	d.close()
	
	try:
		sweeps[window_size][results_count]
	except:
		sweeps[window_size] = {results_count:{'now_finished':[],'yet_unfinished':[]}}
	
	try:
		d=open("finished_plays-%s-%s" %(window_size,results_count),'r')
		t=d.read()
		finished_plays = [i for i in t.split('\n') if i != '']		
		sweeps[window_size][results_count]['now_finished']=finished_plays
		d.close()
	except:
		d=open("finished_plays-%s-%s" %(window_size,results_count),'w')
		d.close()
	try:	
		os.remove("play_boundary_unfinished-%s-%s" %(window_size,results_count))
	except:
		pass
	checkpoint_files = [i for i in os.listdir('.') if "checkpoint-" in i and "-%s-%s" %(window_size,results_count) in i]
	for filename in checkpoint_files:
		d= open(filename,'r')
		play = re.search("(?<=checkpoint-)[a-z|_|0-9]+",filename).group(0)
		check=d.read()
		d.close()
		
		play_endline = all_plays[play][1]
		
		if int(check)>=int(play_endline):
			sweeps[window_size][results_count]['now_finished'].append(play)
			os.remove("checkpoint-%s-%s-%s" %(play,window_size,results_count))
			e = open("finished_plays-%s-%s" %(window_size,results_count),'a')
			outstring = "%s\n" %play
			e.write(outstring)
			e.close()
		else:
			sweeps[window_size][results_count]['yet_unfinished'].append(play)
			e = open("play_boundary_unfinished-%s-%s" %(window_size,results_count),'a')
			outstring = "%s,%s,%s\n" %(play,check,all_plays[play][1])
			e.write(outstring)
			e.close()
	os.remove(outfile)


print "processed:"
print sweeps

