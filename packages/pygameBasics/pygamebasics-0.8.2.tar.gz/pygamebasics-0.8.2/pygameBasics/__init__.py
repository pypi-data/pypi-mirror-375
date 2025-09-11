# DEVELOPER = "beast.barnwal"

import time
import math
import os
import random
import sys
import threading
import inspect
import functools
import string
from safeImport import safe_import
import atexit
asteval = safe_import('asteval')
pygame = safe_import('pygame')
mouse = safe_import('mouse')
keyboard = safe_import('keyboard')
pyautogui = safe_import('pyautogui')

class CORE:
	ENTITIES = []
	SCRIPTS = {}
	SCREEN = None
	CLOCK = None
	KEYS = None
	EVENTS = None
	BROADCASTS = {}
	RUNNING = False
	STAMPS = []
	CALLER_GLOBALS = {}
	WIN = None

if  __name__ != '__main__':
	CORE.RUNNING = False
	CORE.CALLER_GLOBALS = inspect.stack()[1].frame.f_globals
else:
	CORE.CALLER_GLOBALS = globals()

class GUI:
	k = keyboard
	m = mouse
	g = pyautogui

G = GUI

def wait(sec):
	time.sleep(sec)

def getGlobalGibbrish(v):
	if not getattr(CONFIG, 'aeval', False):
		setattr(CONFIG, 'aeval', asteval.Interpreter(symtable=CORE.CALLER_GLOBALS, use_numpy=False))
	
	CONFIG.aeval.symtable.update(CORE.CALLER_GLOBALS)
	return CONFIG.aeval(v)

def getGlobal(v):
	if not hasattr(CONFIG, 'dangerousEval'): setattr(CONFIG, 'dangerousEval', ['__import__', 'os.', 'subprocess.'])
	if any(d in v for d in CONFIG.dangerousEval):
		print("WARNING: Potentially Dangerous getGlobal Call Detected!")
		return None
	return eval(v, CORE.CALLER_GLOBALS)

def getGlobalOld(v):
	def _print(*args, **kwargs):
		""" Debug Print: Add '#' before print below to hide debug messages """
		#print(*args, **kwargs)
		pass

	temp = []
	val = ''

	def get(r):
		nonlocal temp, val
		_print('get(r) done at:    ', r)

		if '[' in r and ']' == r[len(r)-1]:
			idx = r.index('[')
			_idx = len(r) - [t for t in [_ for _ in r].__reversed__()].index(']')
			temp.append(r[:idx])
			_print('indexed new lists:    ', r[idx:_idx], '\t', r[idx+1:_idx-1])
			_print('temp current:    ', temp)
			_print('r:    ', r)
			if '[' == r[idx:_idx][0] and ']' in r[idx+1:_idx-1]:
				ti = r.index(']')
				_print('got ] location index:    ', ti)
				r = r[:ti] + r[ti+1:]
				_print('list after removing]:    ', r)
				get(r[idx+1:_idx])
			else:
				get(r[idx+1:_idx-1])
		
		elif '.' in r:
			parts = r.split('.')
			for part in parts:
				get(part)
		else:
			temp.append(r)
			temp = list(map(lambda x: x.strip("""'"""), temp))
			_print('list generated:    ', temp)
			val = CORE.CALLER_GLOBALS[temp[0]]
			for ab in temp[1:]:
				_print('val beg:    ', val)
				if isinstance(val, dict):
					val = val[ab]
				else:
					val = getattr(val, ab) if hasattr(val, ab) else val[eval(ab)]
				val = val[eval(ab.strip("""'"""))]
				_print('val end:    ', val, end='\n\n')
			_print('val prepared:    ', val)
			return

	get(v)
	_print('value got:   ', val)
	return val
getG = getGlobal

def exportDecorator(func):
	@functools.wraps(func)
	def wrapper(*args, **kwargs):
		#global CORE.CALLER_GLOBALS
		result = func(*args, **kwargs)
		
		for item in globals().keys():
			if not item in ['__name__', '__all__', func.__name__]:
				CORE.CALLER_GLOBALS[item] = globals()[item]
				
		return result
	return wrapper

class paths:
	if __name__ == '__main__':
		base_path = r"C:\Users\Siddharth\Pictures\pictures"
		image1 = os.path.join(base_path, 'DP.jpg')
		image2 = os.path.join(base_path, 'DP_circle.png')

class WINDOW:
	WIDTH = 1200
	HEIGHT = 600
	w = WIDTH
	h = HEIGHT
	size = (w,h)
	
class CONFIG:
	WINDOWTITLE = 'BeastBrine'
	WINDOWLOGO = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Logo.png')
	debug = False
	def atExit():
		pass
	#atExit = lambda: print('', end='')
	size = 40
	speed = 4
	centerX, centerY = 0, 0
	stampSpamMode = False
	showMask = False
	backgroundColor = (255, 255, 255)
	LOG = ''
	FPS = 60
	smoothWait = 0.1
	class strings:
		a2z = 'abcdefghijklmnopqrstuvwxyz'
		A2Z = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
		num = '0123456789'
		allChar = a2z + A2Z + num
		alph = a2z + A2Z	
	key_map = {
		"Player1": (pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d, pygame.K_e, pygame.K_z, pygame.K_x, pygame.K_LSHIFT),
		"Player2": (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_0, pygame.K_5, pygame.K_2, pygame.K_RSHIFT),
	}
	class mouse:
		x = 0
		y = 0
		down = False
		clicked = False
	noCollide = ['Text', 'Box', 'Stamp', 'Line', 'Polygon']
	class screen:
		WIDTH = G.g.size()[0]
		HEIGHT = G.g.size()[1]
		w = WIDTH
		h = HEIGHT
		size = (w,h)
		costumeFormat = []
	dotCostume = None
	#dotCostume.hide()

class temp:
	for x in string.ascii_lowercase:
		globals()[x] = None
	
t = temp

def SMOOTH(smooth=None):
	if not smooth: smooth = CONFIG.smoothWait
	wait(smooth)

class colors:
	RED = (255, 0, 0)
	WHITE = (255, 255, 255)
	GREEN = (0, 255, 0)
	BLUE = (0, 0, 255)
	CYAN = (0, 255, 255)
	YELLOW = (255, 255, 0)
	PURPLE = (255, 0, 255)
	BLACK = (0, 0, 0)

def startConfigSync(data_dict):
	data_dict = getG(data_dict)
	def main():
		while True:
			for key in data_dict.keys():
				try:
					data_dict[key] = getG(key)
				except Exception as e:
					print(f'SYNC ERROR:    {e}')
			
			SMOOTH()
	
	Script(main)

def limit(value, _min, _max):
	return max(_min, min(_max, value))

def roughScript(target):
	threading.Thread(target=target, daemon=True).start()

class Script:
	def __init__(self, function, starter='CORE.RUNNING', once=True, loop=None):
		#global CORE.SCRIPTS
		self.function = function
		self.starter = starter
		self.once = once
		if loop is not None: self.once = not loop

		def main(target):
			#global CORE.CALLER_GLOBALS
			#with threading.Lock():
			for _ in range(1): # used to just run the code below: to prevent unnecessary indentation every time debugging
				while True:
					if getG(target.starter):
						try:
							target.function()
						except ZeroDivisionError:
						#except Exception as e:
							if CORE.RUNNING: print(f"SCRIPT ERROR:    {e}\n	(In {self.function.__name__})\n")
							break
						
						if target.starter == 'CORE.RUNNING' or target.once: break
						
						SMOOTH()
				del CORE.SCRIPTS[target.name]

		self.name = ''.join(random.choices(CONFIG.strings.alph, k=25))
		CORE.SCRIPTS[self.name] = main

		threading.Thread(target=lambda: CORE.SCRIPTS[self.name](self), daemon=True).start()

#@exportDecorator
def INITIALIZE():
	#global CORE.SCREEN, CORE.CLOCK, CORE.RUNNING, CORE.WIN, CORE.ENTITIES, CORE.SCRIPTS, CORE.BROADCASTS, CORE.CALLER_GLOBALS, CORE.STAMPS
	
	CORE.CALLER_GLOBALS = inspect.stack()[1].frame.f_globals
	atexit.register(lambda: CONFIG.atExit())
	
	CORE.WIN = WINDOW()
	CONFIG.centerX, CONFIG.centerY = CORE.WIN.w // 2, CORE.WIN.h // 2
	pygame.init()
	pygame.font.init()
	pygame.mixer.init()
	CORE.RUNNING = True

	CORE.ENTITIES = []
	CORE.SCRIPTS = {}
	CORE.STAMPS = []
	
	CORE.SCREEN = pygame.display.set_mode(CORE.WIN.size)
	setattr(CONFIG, 'ICON', pygame.image.load(CONFIG.WINDOWLOGO))
	pygame.display.set_icon(CONFIG.ICON)
	CORE.CLOCK = pygame.time.Clock()
	CORE.BROADCASTS = {'clonesCreated' : False}
	
	tmpsurf = pygame.Surface((2,2), pygame.SRCALPHA)
	pygame.draw.circle(tmpsurf, (0,0,0), (1,1), 1)
	pygame.image.save(tmpsurf, 'dot.png')
	
	CONFIG.dotCostume = 'dot.png'
	
	CORE.CALLER_GLOBALS['CORE'] = CORE
	os.makedirs(fr'.\assets\{getGlobal("__APPNAME__")}', exist_ok=True)
	
	def varsScript():
		clock = pygame.time.Clock()
		while CORE.RUNNING:
			CONFIG.mouse.x, CONFIG.mouse.y = pygame.mouse.get_pos()
			clock.tick(CONFIG.FPS*0.75)
	
	roughScript(varsScript)
	#for _ in ['SCREEN', 'CORE.WIN', 'ENTITIES', 'SCRIPTS', 'BROADCASTS', 'RUNNING', 'CLOCK']:
	#	CORE.CALLER_GLOBALS[_] = globals()[_]

def remove_transparent_pixels(image):
	image = image.convert_alpha()
	mask = pygame.mask.from_surface(image)
	new_surface = pygame.Surface(image.get_size(), pygame.SRCALPHA)
	for x in range(image.get_width()):
		for y in range(image.get_height()):
			if mask.get_at((x,y)):
				new_surface.set_at((x,y), image.get_at((x,y)))	
	return new_surface

def BASICDRAW(self, SCREEN, x=None, y=None):
	if x is not None: self.x = x
	if y is not None: self.y = y
	verifyAttributes(self)
	
	self.rect = self.image.get_rect(topleft=(self.x, self.y))
	if self.image is None:
		self.color = (*self.color[:3], 255-self.transparency)
		rotated_surf = pygame.Surface((self.sizeX, self.sizeY), pygame.SRCALPHA)
		rotated_surf.fill(self.color)
	else:
		self.image.set_alpha(255-self.transparency)
		if self.type != 'Image': self.image.fill(self.color)
		try:
			rotated_surf = self.get_surface()
		except AttributeError:
			rotated_surf = BASICGETSURFACE(self)

	if not self.centered:
		rotated_rect = rotated_surf.get_rect(center=(self.x + self.sizeX // 2, self.y + self.sizeY // 2))
	else:
		rotated_rect = rotated_surf.get_rect(center=(self.x, self.y))
	
	brightness_surface = pygame.Surface(rotated_surf.get_size(), pygame.SRCALPHA)
	if self.brightness > 0:
		brightness_surface.fill((self.brightness, self.brightness, self.brightness, 0))
		rotated_surf.blit(brightness_surface, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
		CONFIG.LOG = 'brightness done'
	elif self.brightness < 0:
		brightness_surface.fill((abs(self.brightness), abs(self.brightness), abs(self.brightness), 0))
		rotated_surf.blit(brightness_surface, (0,0), special_flags=pygame.BLEND_RGBA_SUB)
		CONFIG.LOG = 'darkness done'

	SCREEN.blit(rotated_surf, rotated_rect.topleft)

	if CONFIG.showMask:
		mask_surf = pygame.mask.from_surface(rotated_surf).to_surface(setcolor=(255, 0, 0, 160), unsetcolor=(0,0,0, 60))
		SCREEN.blit(mask_surf, rotated_rect.topleft)

def BASICGETSURFACE(self):
	verifyAttributes(self)
	
	if self.image:
		rotated_surf = pygame.transform.rotate(self.image, -self.direction)
		return rotated_surf
	
	rect_surf = pygame.Surface((self.sizeX, self.sizeY), pygame.SRCALPHA)
	pygame.draw.rect(rect_surf, self.color, (0, 0, self.sizeX, self.sizeY))
	rotated_surf = pygame.transform.rotate(rect_surf, -self.direction)
	return rotated_surf


class Entity:
	def __init__(self, costumes=[], centered=False, size=None, sizeX=None, sizeY=None, color=colors.BLACK, shape='rect', x=None, y=None, type='Entity', name=None, image=None, hidden=False, variables=None, attributes=[], collider=None, sounds={}):
		self.name = name
		self.transparency = 0
		self.brightness = 0
		self.x =  CONFIG.centerX if x is None else x
		self.y = CONFIG.centerY if y is None else y
		self.direction = 0
		self.shape, self.color, self.type = shape, color, type
		self.sizeX, self.sizeY = size if size else sizeX, size if size else sizeY
		self.sizeX, self.sizeY = 0 if not sizeX else sizeX, 0 if not sizeY else sizeY
		self.image = remove_transparent_pixels(pygame.image.load(image).convert_alpha()) if image else None
		self.image_path = image
		self.hidden = hidden
		self.config = attributes
		self.old_sizeX, self.old_sizeY, self.old_x, self.old_y, self.old_direction = None, None, None, None, None
		self.clones, self.variables = [], {} if not variables else variables
		self._vars = self.variables
		self.isRect = True if not self.image else False
		self._vars['collider'] = collider
		self.deleted = False
		self.stamps = []
		self.costumes = costumes if costumes else []
		self.boxCord = self.x + 130, self.y + 5, 150, 40
		self.centered = centered
		self.costumeIdx = 0
		
		if len(self.costumes) == 0: self.costumes.append(CONFIG.dotCostume.copy())
		self.costume = self.costumes[self.costumeIdx]
		self.loadCostume()
		
		if self.image:
			self.sizeX = self.image.get_width()
			self.sizeY = self.image.get_height()
			self.mask = pygame.mask.from_surface(self.image)
		else:
			self.image = pygame.Surface((self.sizeX, self.sizeY)).convert()
			self.image.fill(self.color)
			self.mask = None

		self.rect = self.image.get_rect(topleft=(self.x, self.y))
		self.original_image = self.image.copy()
		self.originalSize = (self.sizeX, self.sizeY)

		if self.type != "Stamp":
			if 'start at random position' in self.config:
				tmp = 0
				while self.check_collisions() and tmp < 10:
					self.x = random.randint(0, CORE.WIN.w - self.sizeX)
					self.y = random.randint(0, CORE.WIN.h - self.sizeY)
					tmp += 1
				del tmp

		if self.type != "Stamp":
			CORE.ENTITIES.append(self)
		else:
			CORE.STAMPS.append(self)
	
	def loadCostume(self, idx=None):
		if idx is None: idx = self.costume
		self.costumeIdx = idx % len(self.costumes)
		self.costume = self.costumes[self.costumeIdx]
		cost = self.costume.object
		self.image = cost.image
		self.sizeX = cost.sizeX
		self.sizeY = cost.sizeY
		self.type = cost.type
		self.originalSize = cost.originalSize
		self.original_image = cost.original_image
	
	def nextCostume(self):
		self.costumeIdx += 1
		self.loadCostume()
	
	def previousCostume(self):
		self.costumeIdx -= 1
		self.loadCostume()
	
	def addCostume(self, obj):
		self.costumes.append(obj)
	
	def removeCostume(self, idx):
		self.costumes.pop(idx)
	
	def touching(self, other):
		if other == '__mouse__':
			'''
			if CONFIG.mouse.x > self.x and CONFIG.mouse.y > self.y:
				if CONFIG.mouse.x < ((CONFIG.screen.w - CORE.WIN.w)/2 + self.x + self.sizeX):
					if CONFIG.mouse.y < ((CONFIG.screen.h - CORE.WIN.h)/2 + self.y + self.sizeY):
						return True
			return False
			'''
			
			if not self.rect.collidepoint(CONFIG.mouse.x, CONFIG.mouse.y):
				return False
			elif not self.mask:
				return True
			
			relative_x = CONFIG.mouse.x - self.rect.x
			relative_y = CONFIG.mouse.y - self.rect.y

			return self.mask.get_at((relative_x, relative_y))
	
		if self.mask and other.mask:
			offset = (other.rect.x - self.rect.x, other.rect.y - self.rect.y)
			return self.mask.overlap(other.mask, offset) is not None

		return self.rect.colliderect(other.rect)

	def check_collisions(self, _old_x=None, _old_y=None, _old_sizeX=None, _old_sizeY=None, _old_direction=None):
		if self._vars['collider'] == None:
			return False

		for entity in CORE.ENTITIES:
			if entity != self and entity.type not in CONFIG.noCollide and self.touching(entity):
				if _old_x is not None and _old_y is not None:
					self.x, self.y = _old_x, _old_y
				if _old_sizeX is not None and _old_sizeY is not None:
					self.sizeX, self.sizeY = _old_sizeX, _old_sizeY
				if _old_direction is not None:
					self.direction = _old_direction
				return True
		return False

	def changeXby(self, steps):
		self.x += steps
	chx = changeXby
	
	def changeYby(self, steps):
		self.y -= steps
	chy = changeYby

	def move(self, steps):
		dir = math.radians(self.direction)
		self.old_x, self.old_y = self.x, self.y

		self.changeXby(math.sin(dir) * steps)
		self.check_collisions(_old_x=self.old_x, _old_y=self.y)
		self.changeYby(math.cos(dir) * steps)
		self.check_collisions(_old_x=self.x, _old_y=self.old_y)

	def turn(self, deg):

		self.old_direction = self.direction
		self.direction += deg
		self.check_collisions(_old_direction=self.old_direction)

	def changeSize(self, value):
		self.old_sizeX, self.old_sizeY = self.sizeX, self.sizeY
		new_sizeX, new_sizeY = max(1, self.sizeX * (100 + value)/100), max(1, self.sizeY * (100 + value)/100)
		
		if self.image:
			self.image = pygame.transform.smoothscale(self.original_image, (new_sizeX, new_sizeY))

		self.sizeX, self.sizeY = new_sizeX, new_sizeY
		self.check_collisions(self.old_sizeX, self.old_sizeY)
	chs = changeSize
	
	def setSize(self, value):
		self.old_sizeX, self.old_sizeY = self.sizeX, self.sizeY
		new_sizeX, new_sizeY = max(1, self.originalSize[0] * (value)/100), max(1, self.originalSize[1] * (value)/100)
		
		if self.image:
			self.image = pygame.transform.smoothscale(self.original_image, (new_sizeX, new_sizeY))

		self.sizeX, self.sizeY = new_sizeX, new_sizeY
		self.x -= (new_sizeX - self.old_sizeX) / 2
		self.y -= (new_sizeY - self.old_sizeY) / 2
		self.check_collisions(self.old_sizeX, self.old_sizeY)

	def isClicked(self):
		if CONFIG.mouse.down:
			return self.touching('__mouse__')
		return False

	def update(self, keys):
		if not self.type.startswith("Player"):
			return

		self.old_x, self.old_y, self.old_sizeX, self.old_sizeY = self.x, self.y, self.sizeX, self.sizeY
	
		UP, DOWN, LEFT, RIGHT, STAMP, GROW, SHRINK = CONFIG.key_map[self.name]

		if keys[UP]: self.move(1)
		if keys[DOWN]: self.move(-1)
		if keys[LEFT]: self.turn(-5)
		if keys[RIGHT]: self.turn(5)
		if keys[STAMP] and CONFIG.stampSpamMode: self.stamp()
		if keys[GROW]: self.changeSize(2)
		if keys[SHRINK]: self.changeSize(-2)

		self.x = min(CORE.WIN.w, max(0, self.x))
		self.y = min(CORE.WIN.h, max(0, self.y))

	def get_surface(self):
		return BASICGETSURFACE(self)
	
	def draw(self, SCREEN):
		self.boxCord = self.x + 130, self.y + 5, 150, 40
		#self.costume.draw()
		BASICDRAW(self, SCREEN)
		
		'''
		self.rect = self.image.get_rect(topleft=(self.x, self.y))
		if self.image is None:
			self.color = (*self.color[:3], 255-self.transparency)
			rotated_surf = pygame.Surface((self.sizeX, self.sizeY), pygame.SRCALPHA)
			rotated_surf.fill(self.color)
		else:
			self.image.set_alpha(255-self.transparency)
			if self.isRect: self.image.fill(self.color)
			rotated_surf = self.get_surface()

		if not self.centered:
			rotated_rect = rotated_surf.get_rect(center=(self.x + self.sizeX // 2, self.y + self.sizeY // 2))
		else:
			rotated_rect = rotated_surf.get_rect(center=(self.x, self.y))
		
		brightness_surface = pygame.Surface(rotated_surf.get_size(), pygame.SRCALPHA)
		if self.brightness > 0:
			brightness_surface.fill((self.brightness, self.brightness, self.brightness, 0))
			rotated_surf.blit(brightness_surface, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
			CONFIG.LOG = 'brightness done'
		elif self.brightness < 0:
			brightness_surface.fill((abs(self.brightness), abs(self.brightness), abs(self.brightness), 0))
			rotated_surf.blit(brightness_surface, (0,0), special_flags=pygame.BLEND_RGBA_SUB)
			CONFIG.LOG = 'darkness done'

		SCREEN.blit(rotated_surf, rotated_rect.topleft)

		if CONFIG.showMask:
			mask_surf = pygame.mask.from_surface(rotated_surf).to_surface(setcolor=(255, 0, 0, 160), unsetcolor=(0,0,0, 60))
			SCREEN.blit(mask_surf, rotated_rect.topleft)
		'''
	
	def stamp(self, _vars=None, ret=False):
		stamp_entity = Entity(sizeX=self.sizeX, sizeY=self.sizeY, color=self.color, shape=self.shape, x=self.x, y=self.y, type='Stamp', name=self.name, variables=_vars, image=self.image_path)
		stamp_entity.direction = self.direction
		stamp_entity.brightness = self.brightness
		stamp_entity.transparency = self.transparency
		self.stamps.append(stamp_entity)
		if ret:
			return stamp_entity
		
	def createClone(self, ret=False, config=None):
		if not config: config = self.config
		clone = Entity(sizeX=self.sizeX, sizeY=self.sizeY, color=self.color, shape=self.shape, x=self.x, y=self.y, type='Clone', name=self.name, image=self.image_path, variables=self.variables.copy(), attributes=config)
		clone.direction = self.direction
		clone.brightness = self.brightness
		clone.transparency = self.transparency
		clone.costumes = self.costumes
		self.clones.append(clone)
		if ret:
			return clone

	def askAndWait(self, question):
		box = Box('input', *self.boxCord, prompt=question + ' ')
		response = box.response
		del box
		return response
		
	def sayFor(self, text, timeout=1):
		Box('sayFor', *self.boxCord, prompt=text, _vars={'timeout':timeout})
		
	def say(self, text):
		Box('say', *self.boxCord, prompt=text, _vars={'target':self})
	
	def hide(self):
		self.hidden = True
	
	def show(self):
		self.hidden = False

class Entity00:
	def __init__(self, dotCost=False, initialDot=False, costumes=[], centered=False, size=None, sizeX=None, sizeY=None, color=colors.BLACK, shape='rect', x=None, y=None, type='Entity', name=None, image=None, hidden=False, variables=None, attributes=[], collider=None, sounds={}):
		self.name = name
		self.transparency = 0
		self.brightness = 0
		self.x =  CONFIG.centerX if x is None else x
		self.y = CONFIG.centerY if y is None else y
		self.direction = 0
		self.shape, self.color, self.type = shape, color, type
		self.sizeX, self.sizeY = size if size else sizeX, size if size else sizeY
		self.sizeX, self.sizeY = 0 if not sizeX else sizeX, 0 if not sizeY else sizeY
		self.image = remove_transparent_pixels(pygame.image.load(image).convert_alpha()) if image else None
		self.image_path = image
		self.hidden = hidden
		self.config = attributes
		self.old_sizeX, self.old_sizeY, self.old_x, self.old_y, self.old_direction = None, None, None, None, None
		self.clones, self.variables = [], {} if not variables else variables
		self._vars = self.variables
		self.isRect = True if not self.image else False
		self._vars['collider'] = collider
		self.deleted = False
		self.stamps = []
		self.boxCord = self.x + 130, self.y + 5, 150, 40
		self.centered = centered
		if not self.type == 'text':
			self.costumes = costumes if costumes else []
			self.costumeIdx = 0
		
		'''
		if not initialDot:
			if len(self.costumes) == 0:
				if not dotCost:
					self.costumes.append(CONFIG.dotCostume.copy(dotCost=True))
					self.costume = self.costumes[self.costumeIdx]
					self.loadCostume()
		'''
		
		if self.image:
			self.sizeX = self.image.get_width()
			self.sizeY = self.image.get_height()
			self.mask = pygame.mask.from_surface(self.image)
		elif self.sizeX and self.sizeY:
			#self.image = pygame.Surface((self.sizeX, self.sizeY)).convert()
			#self.image.fill(self.color)
			#self.mask = None
			self.image = Rectangle(self.x, self.y, self.sizeX, self.sizeY, self.color)
			self.image_path = os.path.join('assets', getGlobal('__APPNAME__'), f'{"".join(random.choices(CONFIG.strings.alph, k=25))}.png')
			pygame.image.save(self.image.image, self.image_path)
		
		if self.image:
			self.costumes.append(Image(x=self.x, y=self.y, path=self.image_path))
		elif self.sizeX and self.sizeY:
			#self.costumes.append(Polygon([(self.x, self.y), (self.x+sizeX, self.y), (self.x+self.sizeX + self.y+self.sizeY), (self.x, self.y+self.sizeY)], color=self.color))
			self.costumes.append(Image(x=self.x, y=self.y, path=CONFIG.dotCostume))
		
		if not self.type == 'text': 
			self.costumeIdx = len(self.costumes)-1
			self.costume = self.costumes[self.costumeIdx]
			self.loadCostume()
			
			self.rect = self.image.get_rect(topleft=(self.x, self.y))
			self.original_image = self.image.copy()
			self.originalSize = (self.sizeX, self.sizeY)
			
		if self.type != "Stamp":
			if 'start at random position' in self.config:
				tmp = 0
				while self.check_collisions() and tmp < 10:
					self.x = random.randint(0, CORE.WIN.w - self.sizeX)
					self.y = random.randint(0, CORE.WIN.h - self.sizeY)
					tmp += 1
				del tmp

		if self.type != "Stamp":
			CORE.ENTITIES.append(self)
		else:
			CORE.STAMPS.append(self)
	
	def copy(self, dotCost=False):
		copy = Entity(dotCost=dotCost)
		for prop in vars(self):
			setattr(copy, prop, getattr(self, prop))
		
		return copy
	
	def loadCostume(self, idx=None):
		if idx is None: idx = self.costumeIdx
		self.costumeIdx = idx % len(self.costumes)
		self.costume = self.costumes[self.costumeIdx]
		cost = self.costume
		self.image = cost.image
		self.sizeX = cost.sizeX
		self.sizeY = cost.sizeY
		self.type = cost.type
		self.originalSize = cost.originalSize
		self.original_image = cost.original_image
	
	def nextCostume(self):
		self.costumeIdx += 1
		self.loadCostume()
	
	def previousCostume(self):
		self.costumeIdx -= 1
		self.loadCostume()
	
	def addCostume(self, obj):
		self.costumes.append(obj)
	
	def removeCostume(self, idx):
		self.costumes.pop(idx)
	
	def touching(self, other):
		if other == '__mouse__':
			if not self.rect.collidepoint(CONFIG.mouse.x, CONFIG.mouse.y):
				return False
			elif not self.mask:
				return True
			
			relative_x = CONFIG.mouse.x - self.rect.x
			relative_y = CONFIG.mouse.y - self.rect.y

			return self.mask.get_at((relative_x, relative_y))
	
		if self.mask and other.mask:
			offset = (other.rect.x - self.rect.x, other.rect.y - self.rect.y)
			return self.mask.overlap(other.mask, offset) is not None

		return self.rect.colliderect(other.rect)

	def check_collisions(self, _old_x=None, _old_y=None, _old_sizeX=None, _old_sizeY=None, _old_direction=None):
		if self._vars['collider'] == None:
			return False

		for entity in CORE.ENTITIES:
			if entity != self and entity.type not in CONFIG.noCollide and self.touching(entity):
				if _old_x is not None and _old_y is not None:
					self.x, self.y = _old_x, _old_y
				if _old_sizeX is not None and _old_sizeY is not None:
					self.sizeX, self.sizeY = _old_sizeX, _old_sizeY
				if _old_direction is not None:
					self.direction = _old_direction
				return True
		return False

	def changeXby(self, steps):
		self.x += steps
	chx = changeXby
	
	def changeYby(self, steps):
		self.y -= steps
	chy = changeYby

	def move(self, steps):
		dir = math.radians(self.direction)
		self.old_x, self.old_y = self.x, self.y

		self.changeXby(math.sin(dir) * steps)
		self.check_collisions(_old_x=self.old_x, _old_y=self.y)
		self.changeYby(math.cos(dir) * steps)
		self.check_collisions(_old_x=self.x, _old_y=self.old_y)

	def turn(self, deg):
		self.old_direction = self.direction
		self.direction += deg
		self.check_collisions(_old_direction=self.old_direction)

	def changeSize(self, value):
		self.old_sizeX, self.old_sizeY = self.sizeX, self.sizeY
		new_sizeX, new_sizeY = max(1, self.sizeX * (100 + value)/100), max(1, self.sizeY * (100 + value)/100)
		
		if self.image:
			self.image = pygame.transform.smoothscale(self.original_image, (new_sizeX, new_sizeY))

		self.sizeX, self.sizeY = new_sizeX, new_sizeY
		self.check_collisions(self.old_sizeX, self.old_sizeY)
	chs = changeSize
	
	def setSize(self, value):
		self.old_sizeX, self.old_sizeY = self.sizeX, self.sizeY
		new_sizeX, new_sizeY = max(1, self.originalSize[0] * (value)/100), max(1, self.originalSize[1] * (value)/100)
		
		if self.image:
			self.image = pygame.transform.smoothscale(self.original_image, (new_sizeX, new_sizeY))

		self.sizeX, self.sizeY = new_sizeX, new_sizeY
		self.x -= (new_sizeX - self.old_sizeX) / 2
		self.y -= (new_sizeY - self.old_sizeY) / 2
		self.check_collisions(self.old_sizeX, self.old_sizeY)
	ss = setSize
	
	def isClicked(self):
		if CONFIG.mouse.down:
			return self.touching('__mouse__')
		return False

	def update(self, keys):
		if not self.type.startswith("Player"):
			return

		self.old_x, self.old_y, self.old_sizeX, self.old_sizeY = self.x, self.y, self.sizeX, self.sizeY
	
		UP, DOWN, LEFT, RIGHT, STAMP, GROW, SHRINK = CONFIG.key_map[self.name]

		if keys[UP]: self.move(1)
		if keys[DOWN]: self.move(-1)
		if keys[LEFT]: self.turn(-5)
		if keys[RIGHT]: self.turn(5)
		if keys[STAMP] and CONFIG.stampSpamMode: self.stamp()
		if keys[GROW]: self.changeSize(2)
		if keys[SHRINK]: self.changeSize(-2)

		self.x = min(CORE.WIN.w, max(0, self.x))
		self.y = min(CORE.WIN.h, max(0, self.y))

	def get_surface(self):
		return BASICGETSURFACE(self)
	
	def draw(self, SCREEN):
		self.boxCord = self.x + 130, self.y + 5, 150, 40
		#self.costume.draw(SCREEN)
		BASICDRAW(self.costume, SCREEN, x=self.x, y=self.y)
		
	def stamp(self, _vars=None, ret=False):
		stamp_entity = Entity(sizeX=self.sizeX, sizeY=self.sizeY, color=self.color, shape=self.shape, x=self.x, y=self.y, type='Stamp', name=self.name, variables=_vars, image=self.image_path)
		stamp_entity.direction = self.direction
		stamp_entity.brightness = self.brightness
		stamp_entity.transparency = self.transparency
		self.stamps.append(stamp_entity)
		if ret:
			return stamp_entity
		
	def createClone(self, ret=False, config=None):
		if not config: config = self.config
		clone = Entity(sizeX=self.sizeX, sizeY=self.sizeY, color=self.color, shape=self.shape, x=self.x, y=self.y, type='Clone', name=self.name, image=self.image_path, variables=self.variables.copy(), attributes=config)
		clone.direction = self.direction
		clone.brightness = self.brightness
		clone.transparency = self.transparency
		clone.costumes = self.costumes
		self.clones.append(clone)
		if ret:
			return clone

	def askAndWait(self, question):
		box = Box('input', *self.boxCord, prompt=question + ' ')
		response = box.response
		del box
		return response
		
	def sayFor(self, text, timeout=1):
		Box('sayFor', *self.boxCord, prompt=text, _vars={'timeout':timeout})
		
	def say(self, text):
		Box('say', *self.boxCord, prompt=text, _vars={'target':self})
	
	def hide(self):
		self.hidden = True
	
	def show(self):
		self.hidden = False

class Costume:
	def __init__(self, name):
		self.name = name
		self.object = object
	
	def draw(self, SCREEN):
		self.object.draw(SCREEN)

class Image:
	def __init__(self, path, x=None, y=None):
		#super().__init__()
		if x is None: x = CONFIG.centerX
		if y is None: y = CONFIG.centerY
		if not os.path.exists(path):
			print("WARNING: Error Path!")
			return
		self.image = remove_transparent_pixels(pygame.image.load(path).convert_alpha())
		self.x = x
		self.y = y
		self.mask = pygame.mask.from_surface(self.image)
		verifyAttributes(self)
		
		CORE.ENTITIES.append(self)
	
	def draw(self, SCREEN):
		BASICDRAW(self, SCREEN)

class Box(Entity):
	def __init__(self, boxType, x, y, w, h, font=None, prompt='', _vars={}):
		super().__init__(x=x, y=y, sizeX=w, sizeY=h)
		self.size = [x, y, w, h]
		self.rect = pygame.Rect(*self.size)
		self.color_inactive = colors.BLACK
		self.color_active = colors.BLUE
		self.input = ''
		self.prompt = prompt
		self.hidden = False
		self.font = font if font else pygame.font.Font(None, 28)
		self.active = True
		self.variables = _vars
		self._vars = self.variables
		self.type = "Box"
		self.box = boxType
		self.clones = []
		self.entered_text = ''
		self.deleted = False
		self.last_char = ''
		self.last_time = 0
		
		
		if self.box == 'sayFor':
			self.timeout, self.startTime = self._vars['timeout'], time.time()
		elif self.box == 'say':
			self.target = self._vars['target']
			self.target._vars['msg'] = self.prompt
			
		while G.k.is_pressed('enter'):
			pass
		
		while True:
			self.update()
			if self.box == 'input':
				if self.entered_text:
					self.response = self.entered_text
					self.deleted = True
					break
					
			elif self.box == 'sayFor':
				if time.time() - self.startTime > self.timeout:
					self.deleted = True
					break
					
			elif self.box == 'say':
				def boxThread(target):
					while True:
						if target.target._vars['msg'] == '':
							target.deleted = True
							break
						else:
							target.prompt = target.target._vars['msg']
						
				Script(lambda: boxThread(self), 'CORE.RUNNING')

			SMOOTH(CONFIG.smoothWait/5)

	def wrap_text(self, text, font, max_width):
		words = text.split()
		lines = []
		current_line = ''

		for word in words:
			test_line = current_line + ' ' + word if current_line else word
			text_width, _ = font.size(test_line)

			if text_width <= max_width and word != '\n':
				current_line = test_line
			else:
				if current_line: lines.append(current_line)

				while font.size(word)[0] > max_width:
					split_point = len(word) * max_width // font.size(word)[0]
					lines.append(word[:split_point])
					word = word[split_point:]

				current_line = word

		if current_line: lines.append(current_line)
		return lines

	def update(self):
		if G.m.is_pressed('left'):
			self.active = self.rect.collidepoint(CONFIG.mouse.x, CONFIG.mouse.y)
			self.color = self.color_active if self.active else self.color_inactive

		if self.active:		
			for char in [*[_ for _ in CONFIG.strings.a2z], *[_ for _ in CONFIG.strings.num], ' ', 'backspace']:
				if G.k.is_pressed(char):
					if self.last_char == char:
						if time.time() - self.last_time < 0.2:
							continue
					if char != 'backspace': self.input += char
					if char == 'backspace': self.input = self.input[:-1]
					self.last_char = char
					self.last_time = time.time()
					break

			#if G.k.is_pressed('backspace'):
			#	self.input = self.input[:-1]

			if G.k.is_pressed('enter'):
				self.entered_text = self.input
				self.input = ''
				self.active = False

	def draw(self, SCREEN):
		self.color = self.color_active if self.active else self.color_inactive
		self.text = self.prompt + ':' + '\n' + self.input if self.box == 'input' else self.prompt
		max_width = self.size[2] - 10

		lines = self.wrap_text(self.text, self.font, max_width)
		line_height = self.font.get_height()
		self.size[3] =  10 + len(lines) * line_height
		self.rect.size = (self.size[2], self.size[3])

		pygame.draw.rect(SCREEN, colors.WHITE, self.rect)
		pygame.draw.rect(SCREEN, self.color, self.rect, 2)

		for i, line in enumerate(lines):
			text = self.font.render(line, True, self.color)
			SCREEN.blit(text, (self.rect.x + 5, self.rect.y + 5 + i * line_height))

#class Text(Entity):
class Text:
	def __init__(self, text, x, y, font=None, size=40, align='center', color=colors.BLACK, _vars={}):
		#super().__init__(x=x, y=y, size=size)
		self.font = font
		self.size = size
		self.color = color
		self.text = text
		self.x, self.y = x, y
		self.align = align
		self.hidden = False
		self._vars = _vars if _vars else {}
		self.type = "Text"
		self.deleted = False
		self.original_x = self.x
		self.renderText()
		verifyAttributes(self)
		
		CORE.ENTITIES.append(self)   # Already Added in super().__init__()

	def renderText(self):
		try:
			self.FONT = pygame.font.Font(self.font, self.size)
			self.text_surface = self.FONT.render(self.text, True, self.color)
			
			if self.align in ['center', 'centre']: self.x = self.original_x - self.text_surface.get_width() // 2
		except Exception as e:
			print(f'RENDER TEXT ERROR in TEXT {self.text}:    {e}')
		
	def draw(self, SCREEN):
		self.renderText()
		SCREEN.blit(self.text_surface, (self.x, self.y))

	def change(self, name, value):
		if hasattr(self, name):
			setattr(self, name, value)
			#self.renderText()
			if name == 'x': self.original_x = self.x

class Variable(Text):
	def __init__(self, variable, x, y, font=None, size=40, color=colors.BLACK, _vars={}):
		self.variable = variable
		self.x = x
		self.y = y
		self.font = font
		self.size = size
		self.color = color
		self._vars = _vars
		super().__init__(str(getG(self.variable)), self.x, self.y, self.font, self.size, 'center', self.color, self._vars)
		
		def scriptMain(target):
			while not target.deleted:
				new_text = str(getG(self.variable))
				if target.text != new_text: target.change('text', new_text)

				SMOOTH()
				
		Script(lambda: scriptMain(self), 'CORE.RUNNING')
	
	def delete(self):
		self.deleted = True

	def change(self, name, value):
		super().change(name, value)

class Line:
	def __init__(self, cord1, cord2, color=colors.BLACK, width=5):
		#super().__init__()
		self.cords = (tuple(map(int, cord1)), tuple(map(int, cord2)))
		self.color = color
		self.width = width
		self.type = 'Line'
		self.hidden = False
		self.x, self.y = self.cord1
		
		xs = [self.cord1[0], self.cord2[0]]
		ys = [self.cord1[1], self.cord2[1]]
		minX, maxX, minY, maxY = min(xs), max(xs), min(ys), max(ys)
		w,h = maxX - minX + self.width, maxY - minY + self.width
		
		relStart = (self.cord1[0] - minX, self.cord1[1] - minY)
		relEnd = (self.cord2[0] - minX, self.cord2[1] - minY)
		
		self.image = pygame.Surface((w,h), pygame.SRCALPHA)
		pygame.draw.line(self.image, self.color, relStart, relEnd, self.width)
		
		verifyAttributes(self)
		CORE.ENTITIES.append(self)
	
	def draw(self, SCREEN):
		pygame.draw.line(SCREEN, (*self.color, (100-getattr(self, 'transparency', 0))/100), self.cords[0], self.cords[1], self.width)

class Polygon:
	def __init__(self, cords, color=colors.BLACK):
		#super().__init__(initialDot=initial)
		self.cords = cords
		self.color = color
		self.type = 'Polygon'
		self.hidden = False
		self.surface = pygame.Surface(CORE.SCREEN.get_size(), pygame.SRCALPHA)
		verifyAttributes(self)
		if self.type not in CONFIG.noCollide: CONFIG.noCollide.append(self.type)
		
		xCords, yCords = zip(*self.cords)
		minX, maxX, minY, maxY = min(xCords), max(xCords), min(yCords), max(yCords)
		
		self.relativeCords = [(x - minX, y-minY) for x,y in self.cords]
		
		self.x, self.y = minX, minY
		self.image = pygame.Surface((maxX - minX, maxY - minY), pygame.SRCALPHA)
		pygame.draw.polygon(self.image, self.color, self.relativeCords)
		
		CORE.ENTITIES.append(self)
	
	def draw(self, SCREEN):
		pygame.draw.polygon(self.image, (*self.color, (100-getattr(self, 'transparency', 0))), self.cords)
		BASICDRAW(self, SCREEN)
		SCREEN.blit(self.surface, (0,0))

class Rectangle(Polygon):
	def __init__(self, x, y, w, h, color=colors.BLACK):
		super().__init__([(x,y),(x+w,y),(x+w,y+h),(x,y+h)], color=color)

class Triangle(Polygon):
	def __init__(self, cord1, cord2, cord3, color):
		super().__init__([cord1, cord2, cord3], color=color)

class Circle:
	def __init__(self, center, radius, width=5, color=colors.BLACK):
		self.radius = radius
		self.center = center
		self.color = color
		self.hidden = False
		self.width = width
		self.type = 'Circle'
		self.surface = pygame.Surface(CORE.SCREEN.get_size(), pygame.SRCALPHA)
		if self.type not in CONFIG.noCollide: CONFIG.noCollide.append(self.type)
		
		size = 2 * radius + width
		self.image = pygame.Surface((size, size), pygame.SRCALPHA)
		pygame.draw.circle(self.image, self.color, (size//2, size//2), radius, width)
		
		self.x, self.y = self.center[0] - radius, self.center[1] - radius
		verifyAttributes(self)
		CORE.ENTITIES.append(self)
	
	def draw(self, SCREEN):
		#pygame.draw.circle(self.surface, (*self.color, (100-getattr(self, 'transparency', 0))/100), self.center, self.radius, self.width)
		#SCREEN.blit(self.surface, (0,0))
		BASICDRAW(self, SCREEN)

class Group:
	def __init__(self, attributes=None, entities=None):
		attributes, entities = [] if not attributes else attributes, [] if not entities else entities
		self.attributes = attributes
		self.attr = self.attributes
		self.entities = entities
		verifyAttributes(self)
		CORE.ENTITIES.append(self)
	
	def add(self, entity):
		self.entities.append(entity)
	
	def append(self, entity):
		self.add(entity)
		for attr in self.attr:
			setattr(entity, attr, getattr(self, attr, None))
	
	def remove(self, entity):
		if entity in self.entities: self.entities.remove(entity)
	
	def draw(self, SCREEN, attrs='all'):
		for entity in self.entities:
			if attrs == 'all':
				for attr in self.attr:
					setattr(entity, attr, getattr(self, attr, None))
			else:
				setattr(entity, attrs, getattr(self, attrs, None))
	
	def set(self, attr, val=None):
		if attr not in self.attr: self.attr.append(attr)
		setattr(self, attr, val)
		self.draw(None, attrs=attr)

def toggle_mask():
	CONFIG.showMask = not CONFIG.showMask
GUI.k.add_hotkey('t', lambda: toggle_mask() if CONFIG.debug else None)

def updateTerminal():
	while True:
		print(len(CORE.ENTITIES), end='')
		print('\r', end='')

def verifyAttributes(object):
	#if object in CONFIG.verified: return
	def verify(prprt, val):
		nonlocal object
		if not hasattr(object, prprt): setattr(object, prprt, val)
	
	toVerify = [
		'type', 'hidden', 'deleted', 'clones',
		'brightness', 'transparency', 'direction',
		'centered'
	]
	verifyVal = [
		type(object).__name__, False, False, [],
		0, 0, 0,
		True
	]
	
	for prprt, val in zip(toVerify, verifyVal):
		verify(prprt, val)
	
	if not hasattr(object, 'image'): return
	
	toVerify4Image = [
		'mask', 'original_image',
		'originalSize', 'sizeX', 'sizeY'
	]
	verifyVal4Image = [
		pygame.mask.from_surface(object.image), object.image.copy(),
		object.image.get_size(), object.image.get_width(), object.image.get_height()
	]
	
	for prprt, val in zip(toVerify4Image, verifyVal4Image):
		verify(prprt, val)
	
	return
	
	'''
	verify('type', type(object).__name__)
	verify('hidden')
	if not hasattr
	if not hasattr(object, 'type'): setattr(object, 'type', type(object).__name__)
	if not hasattr(object, 'hidden'): setattr(object, 'hidden', False)
	if not hasattr(object, 'deleted'): setattr(object, 'deleted', False)
	if not hasattr(object, 'clones'): setattr(object, 'clones', [])
	if not hasattr(object, 'brightness'): setattr(object, 'brightness', 0)
	if not hasattr(object, 'transparency'): setattr(object, 'transparency', 0)
	
	if hasattr(object, 'image'):
		if not hasattr(object, 'mask'):
			setattr(object, 'mask', pygame.mask.from_surface(object.image))
		if not hasattr(object, 'original_image'):
			setattr(object, 'original_image', object.image.copy())
		if not hasattr(object, 'originalSize'):
			setattr(object, 'originalSize', object.image.get_size())
		if not hasattr(object, 'sizeX'):
			setattr(object, 'sizeX', object.image.get_width())
		if not hasattr(object, 'sizeY'):
			setattr(object, 'sizeY', object.image.get_height())
	#CONFIG.verified.append(object)
	'''
	
def DRAWSCREEN():
	#global CORE.ENTITIES, CORE.SCREEN, CORE.SCRIPTS, CORE.CLOCK, CORE.RUNNING, CORE.WIN, CORE.STAMPS, CORE.KEYS, CORE.EVENTS
			
	CORE.STAMPS = [e for e in CORE.STAMPS if not e._vars.get('erasePerFrame', False)]
	CORE.ENTITIES = [e for e in CORE.ENTITIES if not e.deleted]
	CORE.STAMPS = [e for e in CORE.STAMPS if not e.deleted]
	#CONFIG.verified = [e for e in CONFIG.verified if not e.deleted]
	
	for stamp in CORE.STAMPS:
		if not stamp.hidden:
			stamp.draw(CORE.SCREEN)
	
	for entity in CORE.ENTITIES:	
		if not entity.hidden:
			entity.draw(CORE.SCREEN)
	
	#pygame.display.flip()
	pygame.display.update()

def UPDATEVARS():
	#global CORE.EVENTS, CORE.RUNNING, CORE.ENTITIES
	
	#CONFIG.mouse.x, CONFIG.mouse.y = pygame.mouse.get_pos()
	CORE.KEYS = pygame.key.get_pressed()
		
	CORE.EVENTS = pygame.event.get()
	for event in CORE.EVENTS:
		if event.type == pygame.QUIT:
			CORE.RUNNING = False
			pygame.quit()
			sys.exit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_q:
				CORE.ENTITIES = [e for e in CORE.ENTITIES if e.type != "Stamp"]
			elif event.key == pygame.K_m:
				toggle_mask()
		
		if event.type == pygame.MOUSEBUTTONDOWN:
			CONFIG.mouse.down = True
			CONFIG.mouse.clicked = True
		
		if not event.type == pygame.MOUSEBUTTONDOWN:
			CONFIG.mouse.clicked = False

		if event.type == pygame.MOUSEBUTTONUP:
			CONFIG.mouse.down = False
	
#@exportDecorator
def UPDATE():
	#global CORE.ENTITIES, CORE.SCREEN, CORE.SCRIPTS, CORE.CLOCK, CORE.RUNNING, CORE.WIN, CORE.STAMPS, CORE.KEYS, CORE.EVENTS
	try:
		#threading.Thread(target=DRAWSCREEN, daemon=True)
		pygame.display.set_caption(CONFIG.WINDOWTITLE)
		CORE.SCREEN.fill(CONFIG.backgroundColor)
		
		UPDATEVARS()
		DRAWSCREEN()
		CORE.CLOCK.tick(CONFIG.FPS)
	
	#except ValueError:
	except Exception as e:
		print(f'RUNTIME ERROR:	{e}')
		CORE.RUNNING = False
		pygame.quit()
		sys.exit()

def GAMEPLAY():
	#global CORE.ENTITIES, CORE.SCREEN, CORE.CLOCK, CORE.RUNNING, CORE.EVENTS, CORE.KEYS

	if not CORE.RUNNING: INITIALIZE()

	CORE.RUNNING = True
	CORE.SCREEN = pygame.display.set_mode(CORE.WIN.size)
	pygame.display.set_caption("PYGAME")
	CORE.CLOCK = pygame.time.Clock()

	while CORE.RUNNING:
		CORE.SCREEN.fill(CONFIG.backgroundColor)
		CORE.KEYS = pygame.key.get_pressed()
		if PLAYER1: PLAYER1.update(CORE.KEYS)
		if PLAYER2: PLAYER2.update(CORE.KEYS)

		for entity in CORE.ENTITIES:	
			if entity.type == "Stamp":
				entity.draw(CORE.SCREEN)

		for entity in CORE.ENTITIES:	
			if entity.type != "Stamp" and not entity.hidden:
				entity.draw(CORE.SCREEN)
				for clone in entity.clones:
					clone.draw(CORE.SCREEN)

		pygame.display.flip()
		CORE.EVENTS = pygame.event.get()
		for event in CORE.EVENTS:
			if event.type == pygame.QUIT:
				CORE.RUNNING = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_q:
					CORE.ENTITIES = [e for e in CORE.ENTITIES if e.type != "Stamp"]
				elif not CONFIG.stampSpamMode and event.key == CONFIG.key_map['Player1'][4]:
					PLAYER1.stamp()
				elif not CONFIG.stampSpamMode and event.key == CONFIG.key_map['Player2'][4]:
					PLAYER2.stamp()
				elif event.key == pygame.K_m:
					toggle_mask()

		CORE.CLOCK.tick(60)

	pygame.quit()

def mainloopGAME():
	threading.Thread(target=GAME, daemon=True).start()

if __name__ == '__main__':
	INITIALIZE()

	PLAYER1 = Entity(name='Player1', x=CONFIG.centerX-50, image=paths.image1, attributes=['start at random position'])
	PLAYER2 = Entity(name='Player2', x=CONFIG.centerX+50, image=paths.image2, attributes=['start at random position'])

	GAMEPLAY()

else:
	PLAYER1 = PLAYER2 = None

# DEBUG CONSOLE THREAD
# threading.Thread(target=updateTerminal, daemon=True).start()
