#!/usr/bin/env python2

import os
import shutil

from pythonfiles import Path
from unittest import TestCase

class TestPathManipulations(TestCase):
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

	def testEquality(self):
		self.assertTrue(Path('a', 'b') == Path('a' + os.sep + 'b'))
		self.assertFalse(Path('a', 'b') != Path('a' + os.sep + 'b'))

		self.assertTrue(Path('a', 'b', 'c', os.pardir) == Path('a', 'b'))
		self.assertFalse(Path('a', 'b', 'c', os.pardir) != Path('a', 'b'))

		self.assertFalse(Path('a', 'b') == Path('a', 'b').toAbsolute())
		self.assertTrue(Path('a', 'b') != Path('a', 'b').toAbsolute())

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
		self.assertEqual(
			str(Path('a').toAbsolute()),
			os.path.join(os.getcwd(), 'a')
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

class TestPathOperations(TestCase):
	def setUp(self):
		rootDir = 'testSandbox'

		if os.path.exists(rootDir):
			shutil.rmtree(rootDir)

		os.mkdir(rootDir)

		with open(os.path.join(rootDir, 'empty.txt'), 'w') as f:
			f.write('')

		self.TEST_DIR = rootDir

		rootFindDir = os.path.join(rootDir, 'find')

		findDirs = [
			[],
			['a'],
			['a', 'x'],
			['a', 'y'],
			['a', 'z'],
			['b'],
			['b', 'm'],
			['b', 'n'],
			['c'],
		]
		for path in findDirs:
			os.mkdir(os.path.join(rootFindDir, *path))

		findFiles = [
			['a', 'README.md'],
			['a', 'settings.ini'],
			['a', 'x', 'ax1.js'],
			['a', 'x', 'ax2.js'],
			['a', 'y', 'ay1.js'],
			['a', 'y', '.gitignore'],
			['a', 'z', 'az1.js'],
			['b', 'stuff.js'],
			['b', 'm', 'bm1.js'],
			['c', 'notes.md'],
			['c', 'other.js'],
			['main.js'],
			['overview.md'],
		]
		for path in findFiles:
			with open(os.path.join(rootFindDir, *path), 'w') as f:
				f.write('Contents of ' + path[-1])

		self.FIND_DIRS = findDirs
		self.FIND_FILES = findFiles
		self.FIND_TEST_DIR = rootFindDir

	def testExists(self):
		r = self.TEST_DIR

		self.assertTrue(Path(r).exists())
		self.assertTrue(Path(r).existsAsDirectory())
		self.assertFalse(Path(r).existsAsFile())

		self.assertFalse(Path(r, 'nonexistant').exists())
		self.assertFalse(Path(r, 'nonexistant').existsAsDirectory())
		self.assertFalse(Path(r, 'nonexistant').existsAsFile())

		self.assertFalse(Path(r, 'deeply', 'nonexistant').exists())
		self.assertFalse(Path(r, 'deeply', 'nonexistant').existsAsDirectory())
		self.assertFalse(Path(r, 'deeply', 'nonexistant').existsAsFile())

		self.assertTrue(Path(r, 'empty.txt').exists())
		self.assertFalse(Path(r, 'empty.txt').existsAsDirectory())
		self.assertTrue(Path(r, 'empty.txt').existsAsFile())

	def testMakeDirectory(self):
		r = self.TEST_DIR

		d1 = Path(r, 'dir1')
		d1.makeDirectory(ancestors=True, failOnExist=True)
		self.assertTrue(os.path.isdir(str(d1)))

		d1.makeDirectory(ancestors=True, failOnExist=False)
		self.assertTrue(os.path.isdir(str(d1)))

		d1.makeDirectory(ancestors=False, failOnExist=False)
		self.assertTrue(os.path.isdir(str(d1)))

		self.assertRaises(
			OSError,
			d1.makeDirectory,
			ancestors=False, failOnExist=True
		)

		self.assertRaises(
			OSError,
			d1.makeDirectory,
			ancestors=True, failOnExist=True
		)

		d2d1 = Path(r, 'dir2', 'dir1')
		self.assertRaises(
			OSError,
			d2d1.makeDirectory,
			ancestors=False, failOnExist=False
		)
		d2d1.makeDirectory(ancestors=True, failOnExist=False)
		self.assertTrue(os.path.isdir(str(d2d1)))

		d3d1 = Path(r, 'dir3', 'dir1')
		self.assertRaises(
			OSError,
			d3d1.makeDirectory,
			ancestors=False, failOnExist=True
		)
		d3d1.makeDirectory(ancestors=True, failOnExist=True)
		self.assertTrue(os.path.isdir(str(d3d1)))

		self.assertRaises(
			OSError,
			d3d1.makeDirectory,
			ancestors=True,
			failOnExist=True
		)

	def testFind(self):
		p = Path(self.FIND_TEST_DIR)

		self.assertEqual(
			list(Path(p, 'main.js').find()),
			[Path(p, 'main.js')]
		)

		self.assertEqual(
			sorted([str(f) for f in p.find()]),
			sorted(
				[str(Path(p, *f)) for f in self.FIND_DIRS] +
				[str(Path(p, *f)) for f in self.FIND_FILES]
			)
		)
