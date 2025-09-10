"""Module"""
__version__="1.0.5"
import sys
import time
def pdtf(total,sleep=0,name="Progress",length=10):
	try:
		total2=total.stop
	except:
		print(f"[X]{total}-->[✓]range(int,int)")
		sys.exit()
	for i in range(total.start,total.stop+1):
		iteration=i
		time.sleep(sleep)
		progress=(iteration/total2)
		arrow="█"*int(round(progress*length))
		spaces=" "*(length-len(arrow))
		sys.stdout.write(f"\r{name}:{int(progress * 100)}%|{arrow+spaces}| {int(progress*total.stop)}/{total.stop} ")
		sys.stdout.flush()
	print()
	return total