import unittest
from RSPileScripting.Utilities.ColorPicker import ColorPicker

class TestColorPicker(unittest.TestCase):
	def testInvalidColorSelections(self):
		#test invalid colours
		with self.assertRaises(ValueError):
			ColorPicker.getColorFromRGB(260,50,50)
	
		with self.assertRaises(ValueError):
			ColorPicker.getColorFromRGB(250,350,50)
			
		with self.assertRaises(ValueError):
			ColorPicker.getColorFromRGB(250,50,500)
		
	def testGetRGBFromColor(self):
		self.assertEqual((255,0,0), ColorPicker.getRGBFromColor(ColorPicker.Red))
		self.assertEqual((0,0,255), ColorPicker.getRGBFromColor(ColorPicker.Blue))
		self.assertEqual((0,147,0), ColorPicker.getRGBFromColor(ColorPicker.Green))
		
		#Teal is 0x8E8E38 and its RGB values are (56, 142, 142)
		self.assertEqual((56, 142, 142), ColorPicker.getRGBFromColor(ColorPicker.Teal))

	def testGetColorFromRGB(self):
		self.assertEqual(ColorPicker.getColorFromRGB(56, 142, 142), ColorPicker.Teal)

	def testColorName(self):
		self.assertEqual(ColorPicker.getColorName(ColorPicker.Teal), "Teal")
		self.assertEqual(ColorPicker.getColorName(ColorPicker.Bright_Green), "Bright_Green")
		self.assertEqual(ColorPicker.getColorName(ColorPicker.Lavender), "Lavender")