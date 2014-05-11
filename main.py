import os
import sys
import time

from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.garden.moretransitions import RippleTransition
from kivy.uix.modalview import ModalView
from kivy.uix.togglebutton import ToggleButton
from kivy.properties import OptionProperty, ObjectProperty,StringProperty, \
	NumericProperty, BooleanProperty
import kivy.utils

class SplashScreen(Screen):
	pass
	
class MainScreen(Screen):
	pass

class PresetList(ModalView):
	pass

class InstrumentList(ModalView):
	pass

class Help(ModalView):
	pass

class Pad(ToggleButton):
	state   = OptionProperty('normal', options=('normal', 'down'))
	playing = OptionProperty('off', options=('off', 'on'))
	
	background_normal_off = 'Data/images/button_normal_off.png'
	background_down_off   = 'Data/images/button_down_off.png'
	background_normal_on  = 'Data/images/button_normal_on.png'
	background_down_on    = 'Data/images/button_down_on.png'

	def on(self):
		self.playing = 'on'
		
	def off(self):
		self.playing = 'off'

class Symphonium(App):
	title = "Symphonium"
	icon  = "icon.png"

	rootPath  = os.path.dirname(os.path.realpath(sys.argv[0]))
	imgPath   = rootPath + '/Data/images'
	soundPath = rootPath + '/Data/sound'
	presetPath = rootPath + '/Data/presets'
	
	sounds = []
	
	game_of_life = BooleanProperty(False)
	bpm    = NumericProperty(180)
	paused = BooleanProperty(False)
	instrument = StringProperty('Kalimba')
	
	grid = [[0 for i in range(16)] for i in range(16)]
	current = 0;
	time_last = 0
	max_channels = 4
	
	def build(self):				
		
		self.load_kalimba() #by default
		
		self.screenManager = ScreenManager(transition=RippleTransition(duration=2.0))
		
		self.splash = SplashScreen(name='splash')
		self.main   = MainScreen(name='main')
		for i in range(16):
			for j in range(16):
				pad = Pad(size_hint=(1/16.0,1/16.0))
				self.main.grid.add_widget(pad)
				self.grid[i][j] = pad

		self.preset_list = PresetList()
		self.instrument_list = InstrumentList()
		self.help = Help();
		
		self.screenManager.add_widget(self.splash)
		self.screenManager.add_widget(self.main)
		
		self.showSplash()
		#self.showMain()
		return self.screenManager
		
		
	def showSplash(self):		
		self.screenManager.current = 'splash'
		
		Animation(
			scale=self.splash.background.scale*1.1, 
			duration=15.0
		).start(self.splash.background)
		
		
	def showMain(self):
		self.screenManager.current = 'main'
		
		Clock.schedule_interval(self.play, 60.0/self.bpm)
		
	def load_kalimba(self, *largs):
		#pause ?
		self.instrument = 'Kalimba'
		self.sounds = []
		for c in range(self.max_channels):
			self.sounds.append([])
			for i in range(16):
				soundfile = self.soundPath + "/kalimba/kalimba%s.ogg" % (i+1)
				self.sounds[c].append(SoundLoader.load(soundfile))
			
	def load_oud(self, *largs):
		#pause ?
		self.instrument = 'Oud'
		self.sounds = []
		scale = ('B1', 'C2', 'C#2', 'E2', 'F2', 'G2', 'G#2', 'B2', 'C3', 'C#3', 'E3', 'F3', 'G3', 'G#3', 'B3', 'C4')
		for c in range(self.max_channels):
			self.sounds.append([])
			for i in scale:
				soundfile = self.soundPath + "/oud/oud_%s.ogg" % (i)
				self.sounds[c].append(SoundLoader.load(soundfile))


	def play(self,dt):
		
		if self.time_last != 0:
			pass
			#print("TIC %f" % (time.time() - self.time_last))
		self.time_last = time.time()
		
		for i in range(16):
			self.grid[i][self.current].playing = 'off'
		
		if self.current == 15:
			self.current = 0
			if self.game_of_life:
				self.process_game_of_life()
		else:
			self.current += 1
		
		for i in range(16):
			self.grid[i][self.current].playing = 'on'
			if self.grid[i][self.current].state == 'down':
				#dispatch on X channels to avoid audio glitches
				self.sounds[self.current % self.max_channels][i].stop()
				self.sounds[self.current % self.max_channels][i].play()
				
				# !!!! Sound objects seems to never change its state from to stop, bug ?
				#found = False
				#for c in range(self.max_channels):
				#	#find a free channel
				#	if self.sounds[c][i].state == 'stop':
				#		self.sounds[c][i].play()
				#		print("using channel %d for sound %d" % (c,i))
				#		found = True
				#		break
				#	
				#if found == False:
				#	print("stopping channel 0 of sound %d" % i)
				#	print("using channel 0 for sound %d" % i)
				#	self.sounds[0][i].stop()
				#	self.sounds[0][i].play()


	def reset(self):
		for i in range(16):
			for j in range(16):
				self.grid[i][j].state = 'normal'
				self.grid[i][j].playing = 'off'
		self.current = 0
	
	def toggle_pause(self):
		if self.paused:
			self.paused = False
			Clock.schedule_interval(self.play, 60.0/self.bpm)
		else:
			self.paused = True
			Clock.unschedule(self.play)
	
	def tempo_up(self):
		self.bpm += 10
		Clock.unschedule(self.play)
		Clock.schedule_interval(self.play, 60.0/self.bpm)
	
	def tempo_down(self):
		self.bpm -= 10
		Clock.unschedule(self.play)
		Clock.schedule_interval(self.play, 60.0/self.bpm)
		
	def transpose_up(self):
		for j in range(16):
			save = self.grid[15][j].state
			for i in range(15,0,-1):
				self.grid[i][j].state = self.grid[i-1][j].state
			self.grid[0][j].state = save
		
	def transpose_down(self):
		for j in range(16):
			save = self.grid[0][j].state
			for i in range(15):
				self.grid[i][j].state = self.grid[i+1][j].state
			self.grid[15][j].state = save
		
		
	def toggle_game_of_life(self):
		if self.game_of_life:
			self.game_of_life = False
		else:
			self.game_of_life = True
	
	def process_game_of_life(self):
		
		#copy the original grid
		original_grid= [[0 for i in range(16)] for i in range(16)]
		for x in range(16):
			for y in range(16):
				original_grid[x][y] = self.grid[x][y]
		'''
		1 2 3
		4 X 5
		6 7 8
		'''
		def count_neighbour(x,y):
			count = 0
			#1
			if x>0 and y+1<16 and original_grid[x-1][y+1].state == 'down':
				count +=1
			#2
			if y+1< 16 and original_grid[x][y+1].state == 'down':
				count +=1
			#3
			if x+1< 16 and y+1<16 and original_grid[x+1][y+1].state == 'down':
				count +=1
			#4
			if x>0 and original_grid[x-1][y].state == 'down':
				count +=1
			#5
			if x+1< 16 and original_grid[x+1][y].state == 'down':
				count +=1
			#6
			if x>0 and y-1>0 and original_grid[x-1][y-1].state == 'down':
				count +=1
			#7
			if y-1>0 and original_grid[x][y-1].state == 'down':
				count +=1
			#8
			if x+1<16 and y-1>0 and original_grid[x+1][y-1].state == 'down':
				count +=1
			return count

		for x in range(16):
			for y in range(16):
				count = count_neighbour(x,y)
				#3 neighbours -> alive
				if count == 3:
					self.grid[x][y].state = 'down'
				#2 neighbours -> same state
				elif count == 2:
					pass
				#dead
				else:
					self.grid[x][y].state = 'normal'

	def load_preset(self, preset):
		
		namespace = dict()
		exec(open(self.presetPath + '/'+preset+'.py').read(),namespace)
		
		if self.paused == False:
			self.toggle_pause()
			
		self.reset()
		
		y = 15
		for line in namespace['motif'].split('\n'):
			if line == "":
				continue
			for x in range(16):
				if line[x] == '1':
					self.grid[y][x].state = 'down'
			y -= 1

		if 'instrument' in namespace:
			if namespace['instrument'] == 'kalimba':
				self.load_kalimba();
			if namespace['instrument'] == 'oud':
				self.load_oud();			
		if 'bpm' in namespace:
			self.bpm = namespace['bpm']
		if 'game_of_life' in namespace:
			self.game_of_life = namespace['game_of_life']
		
		self.preset_list.dismiss()
		if self.paused == True:
			self.toggle_pause()

if __name__ in ('__main__', '__android__'):
	Symphonium().run()
