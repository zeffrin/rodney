import time

class NethackMoon:
	def luckmsg(self):
		NEW_MOON = 0;
		FULL_MOON = 4;

		outp = ""   # scope for buffer

		moon = self.phase_of_the_moon()

		if moon is FULL_MOON:
			outp = "You are lucky! Full moon tonight. "
		if moon is NEW_MOON:
			outp = "Be careful! New moon tonight. "

		if self.friday_13th():
			outp = outp + "Watch out! Bad things can happen"\
			" on Friday the 13th."

		return outp
		
	def phase_of_the_moon(self):
		thetime = time.localtime()
		
		diy = thetime[7] - 1     # minus 1 thanks to python using diff range
		goldn = (thetime[0] % 19) + 1
		epact = (11 * goldn + 18) % 30
		if (epact == 25 and goldn > 11) or epact == 24:
			epact = epact + 1

		return ((((((diy + epact) * 6) + 11) % 177) / 22) & 7 )

	def friday_13th(self):
		thetime = time.localtime()

		if thetime[6] == 4 and thetime[2] == 13:
			return True
		else:
			return False


