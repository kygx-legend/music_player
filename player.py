#!/usr/bin/env python   
#-*- coding: utf-8 -*-
#----import----
import os
import sys
import time
import threading
import wx
import wx.lib.buttons as buttons
import pygame,pygame.mixer 
import ConfigParser

#----mainFrame----
class Frame(wx.Frame):   

#----init----
	def __init__(self):
		wx.Frame.__init__(self, None, -1, 'Music Player', size=(800, 600))
		self.conf = ConfigParser.ConfigParser()
		self.conf.read('player.conf')
		#----parameters----
		self.VolumeShow = False
		self.offset = 0
		self.cycle = True
		self.stop = True
		self.select = 0
		self.music_dir = self.conf.get('directory','music_dir')
		self.img_dir = self.conf.get('directory','img_dir')
		#----panel----
		mainPanel = wx.Panel(self, -1)
	 	musicList = self.scan()
	 	self.listBox = wx.ListBox(mainPanel, -1, (0, 0), (680, 420), musicList, wx.LB_SINGLE)
		self.listBox.SetSelection(0)
		self.slider = wx.Slider(mainPanel,wx.NewId(),pos=(0,40),size=(500, -1), style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
		self.slider.SetRange(0,300)
		self.vol = VolumeFrame()
		self.vol.Center()
		stopbmp = self.loadpngandscale(self.conf.get('pngfile','stop'))
		self.stopButton = buttons.GenBitmapButton(mainPanel, -1, stopbmp)
		playbmp = self.loadpngandscale(self.conf.get('pngfile','play'))
		self.playButton = buttons.GenBitmapButton(mainPanel, -1, playbmp)
		pausebmp = self.loadpngandscale(self.conf.get('pngfile','pause'))
		self.pauseButton = buttons.GenBitmapButton(mainPanel, -1, pausebmp)
		unpausebmp = self.loadpngandscale(self.conf.get('pngfile','unpause'))
		self.unpauseButton = buttons.GenBitmapButton(mainPanel, -1, unpausebmp)
		volumebmp = self.loadpngandscale(self.conf.get('pngfile','volume'))
		self.volumeButton = buttons.GenBitmapButton(mainPanel, -1, volumebmp)
	    #----layout----
		HBox = wx.BoxSizer(wx.VERTICAL)
		LBox = wx.BoxSizer(wx.HORIZONTAL)
		LBox.Add(self.listBox, 0)
		RBox = wx.BoxSizer(wx.HORIZONTAL)
		RBox.Add(self.slider, 0)
		BBox = wx.BoxSizer(wx.HORIZONTAL)
		BBox.Add(self.stopButton, 0)
		BBox.Add(self.playButton, 0)
		BBox.Add(self.pauseButton, 0)
		BBox.Add(self.unpauseButton, 0)
		BBox.Add(self.volumeButton, 0)
		HBox.Add(LBox, 0 ,wx.TOP | wx.CENTER, 10)
		HBox.Add((-1, 10))
		HBox.Add(RBox, 0 ,wx.CENTER, 10)
		HBox.Add((-1, 10))
		HBox.Add(BBox, 0 ,wx.BOTTOM | wx.CENTER, 10)
		mainPanel.SetSizer(HBox)
		#----timer----
		self.slider_timer = wx.Timer(self)  
		#----event----
		self.Bind(wx.EVT_BUTTON, self.Play, self.playButton)
		self.Bind(wx.EVT_BUTTON, self.Stop, self.stopButton)
		self.Bind(wx.EVT_BUTTON, self.Pause, self.pauseButton)
		self.Bind(wx.EVT_BUTTON, self.Unpause, self.unpauseButton)
		self.Bind(wx.EVT_BUTTON, self.SetVolume, self.volumeButton)
		self.vol.Bind(wx.EVT_CLOSE, self.CloseVolume)
		self.Bind(wx.EVT_SCROLL, self.OnSeek, self.slider) 
		self.Bind(wx.EVT_TIMER, self.onUpdateSlider,self.slider_timer)  
		self.Bind(wx.EVT_CLOSE, self.Close)
		
#----file operation----
	#----scan the files of mp3----
	def scan(self):
		listFound = os.listdir(self.music_dir)
		listReturn = []
		for li in listFound:
			if li.find('.mp3') > 0 :
				listReturn.append(li)
		listReturn.sort()
		return listReturn

	#----load the png and scale them----
	def loadpngandscale(self, filename):
		tmp = wx.Image(self.img_dir+filename, wx.BITMAP_TYPE_PNG)
		tmp2 = tmp.Scale(tmp.GetWidth()/4, tmp.GetHeight()/4)
		return tmp2.ConvertToBitmap()
	
#----event operation----
	#----play button----
	def Play(self, event):
		self.select = self.listBox.GetSelection()
		self.offset = 0
		self.stop = False
		self.play()

	#----play operation---
	def play(self):
		file = self.music_dir+self.listBox.GetString(self.select)
		file = file.encode("utf8")
		#print file
		pygame.mixer.music.load(file)
		self.slider_timer.Start(100)  
		pygame.mixer.music.play(1, 0.0)

	#----stop button----
	def Stop(self, event):
		self.stop = True
		pygame.mixer.music.stop()
	
	#----pause button----
	def Pause(self, event):
		pygame.mixer.music.pause()
	
	#----unpause button----
	def Unpause(self, event):
		pygame.mixer.music.unpause()

	#----volume button----
	def SetVolume(self, event):
		if not self.VolumeShow:
			self.vol.Show()
			self.VolumeShow = True

	#----close volume frame----
	def CloseVolume(self, event):
		self.vol.Hide()
		self.VolumeShow = False

	#----use the slider to control----
	def OnSeek(self, event):
		self.offset = self.slider.GetValue()
		pygame.mixer.music.stop()
		pygame.mixer.music.play(1, self.offset)

	#----show the time playing and detect if done----
	def onUpdateSlider(self, event):
		if pygame.mixer.music.get_busy():
			offset = pygame.mixer.music.get_pos()/1000.0
			self.slider.SetValue(offset+self.offset) 
		else:
			self.offset = 0
			self.slider.SetValue(0) 
			self.slider_timer.Stop()
			if self.cycle and not self.stop:
				self.select += 1
				if not self.select < self.listBox.GetCount():
					self.select = 0
				self.listBox.SetSelection(self.select)
				self.slider_timer.Start(100)  
				self.play()

	#----when click close----
	def Close(self, event):
		self.Destroy()
		sys.exit()

#----volumeFrame----
class VolumeFrame(wx.MiniFrame):

#----init----
	def __init__(self):
		wx.Frame.__init__(self, None, -1, 'Volume', size=(80, 150))
		panel = wx.Panel(self, -1)
	 	value = pygame.mixer.music.get_volume()*100
	 	self.slider = wx.Slider(panel, wx.NewId(), pos=(25, 5),size=(-1, 130), style=wx.SL_VERTICAL | wx.SL_AUTOTICKS | wx.SL_LABELS )
	 	self.slider.SetRange(0,100)
		self.slider.SetTickFreq(20, 1)
	 	self.slider.SetValue(value)
	 	self.Bind(wx.EVT_SCROLL, self.ChangeVolume, self.slider)  

#----change the volume----
	def ChangeVolume(self, event):
		value = self.slider.GetValue()/100.0
		pygame.mixer.music.set_volume(value)

#----Appliaction----
class App(wx.App):

	def OnInit(self):	
		pygame.mixer.init()
		self.frame = Frame()
		self.frame.Center()
		self.frame.Show()
		return True

#----mainloop----
if __name__ == '__main__':   
	app = App()
	app.MainLoop()
