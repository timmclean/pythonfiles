#!/usr/bin/env python2

import os

from pythonfiles import Path
from unittest import TestCase

class TestPath(TestCase):
	def testConstruct(self):
		# Edge cases
		Path()
		Path('')

		# Absolute not permitted after first part
		self.assertRaises(ValueError, Path, 'a', os.sep + 'x')

	def testToString(self):
		cases = [
			(['a'],                                'a'),
			(['abc' + os.sep + 'def'],             'abc' + os.sep + 'def'),
			(['abc', 'def'],                       'abc' + os.sep + 'def'),
			(['a' + os.sep + 'b', 'c'],            'a' + os.sep + 'b' + os.sep + 'c'),
			(['a', 'b', '..'], 'a'),
		]

		for caseInput, caseOutput in cases:
			self.assertEqual(str(Path(*caseInput)), caseOutput)

		self.assertEqual(str(Path()), str(Path('')))

	def testRepr(self):
		self.assertEqual(
			repr(Path('abc', 'def')),
			'Path(' + repr('abc' + os.sep + 'def') + ')'
		)

	def testAbsVsRel(self):
		absCases = [
			[os.sep],
			[os.sep, 'a'],
			[os.sep + 'a' + os.sep],
			[os.sep + 'a', 'b'],
		]
		relCases = [
			[],
			['a'],
			['a' + os.sep],
			['a', 'b'],
			['a', '..'],
			['..'],
			['..', '..'],
		]

		for case in absCases:
			self.assertTrue(Path(*case).isAbsolute)
			self.assertFalse(Path(*case).isRelative)

		for case in relCases:
			self.assertTrue(Path(*case).isRelative)
			self.assertFalse(Path(*case).isAbsolute)

	def testJoin(self):
		result = Path('a', 'b') + Path('c' + os.sep + 'd')
		self.assertTrue(isinstance(result, Path))
		self.assertEqual(str(result), 'a' + os.sep + 'b' + os.sep + 'c' + os.sep + 'd')

	def testToAbsolute(self):
		self.assertEqual(
			str(Path('b', 'c').toAbsolute(Path(os.sep, 'a'))),
			os.path.join(os.sep, 'a', 'b', 'c')
		)
		self.assertEqual(
			str(Path('..', 'b', 'c').toAbsolute(Path(os.sep, 'x', 'y'))),
			os.path.join(os.sep, 'x', 'b', 'c')
		)

	def testRelativeTo(self):
		self.assertRaises(
			ValueError,
			Path('a').relativeTo,
			Path(os.sep + 'a')
		)
		self.assertRaises(
			ValueError,
			Path(os.sep + 'a').relativeTo,
			Path('a')
		)
		self.assertEqual(
			str(Path('a', 'b').relativeTo(Path('c'))),
			os.path.join('..', 'a', 'b')
		)
		self.assertEqual(
			str(Path('a', 'b').relativeTo(Path('b'))),
			os.path.join('..', 'a', 'b')
		)
		self.assertEqual(
			str(Path().relativeTo(Path('a', 'b'))),
			os.path.join('..', '..')
		)
		self.assertEqual(
			str(Path('..').relativeTo(Path('a', 'b'))),
			os.path.join('..', '..', '..')
		)
		self.assertEqual(
			str(Path('..', 'a', 'b', 'c', 'd').relativeTo(Path('..', 'a', 'b'))),
			os.path.join('c', 'd')
		)
		self.assertEqual(
			str(Path('a', 'b', 'c', 'd').relativeTo(Path('a', 'b'))),
			os.path.join('c', 'd')
		)
		self.assertEqual(
			str(Path('a', 'b').relativeTo(Path())),
			os.path.join('a', 'b')
		)
		self.assertEqual(
			str(Path().relativeTo(Path())),
			str(Path())
		)

	def testParent(self):
		self.assertEqual(
			Path(os.sep).parent,
			None
		)
		self.assertEqual(
			str(Path('.').parent),
			'..'
		)
		self.assertEqual(
			str(Path('..').parent),
			'..' + os.sep + '..'
		)
		self.assertEqual(
			str(Path('..', 'a').parent),
			'..'
		)
		self.assertEqual(
			str(Path('abc').parent),
			'.'
		)
		self.assertEqual(
			str(Path('abc', 'd.txt').parent),
			'abc'
		)
		self.assertEqual(
			str(Path(os.sep, 'a', 'b', 'c.txt').parent),
			os.sep + 'a' + os.sep + 'b'
		)

# /a/b
# /a/b/c.txt
# b
# b/c.txt
