import errno
import os

__all__ = ['Path']

class Path:
	"""
	A representation of a file path that allows easy manipulation.

	As much as possible, path manipulations are done without
	accessing the file system.  This makes it possible to work with paths
	that do not yet access.

	Note: the empty path is a relative path pointing to the directory
	within which relative paths are evaluated.
	If "c" refers to "/a/b/c", then "" refers to "/a/b".
	The empty path is an identity with respect to path joining:
		Path('') + myRelativePath = myRelativePath
		myPath + Path('') = myPath
	"""

	def __init__(self, *parts):
		fullPath = ''

		for i, part in enumerate(parts):
			if i > 0 and os.path.isabs(part):
				prevPart = parts[i - 1]
				raise ValueError(
					'Cannot join %s and %s' % (repr(prevPart), repr(part))
				)

			if isinstance(part, Path):
				fullPath = os.path.join(fullPath, part._value)
			elif isinstance(part, basestring):
				fullPath = os.path.join(fullPath, part)

		self._value = os.path.normpath(fullPath)

	def __str__(self):
		return self._value

	def __repr__(self):
		return 'Path(%s)' % repr(self._value)

	def __eq__(self, another):
		if not isinstance(another, Path):
			return NotImplemented

		return self._value == another._value

	def __ne__(self, another):
		if not isinstance(another, Path):
			return NotImplemented

		return self._value != another._value

	@property
	def isAbsolute(self):
		return os.path.isabs(self._value)

	@property
	def isRelative(self):
		return not self.isAbsolute

	def __add__(self, descendent):
		if not isinstance(descendent, Path):
			return NotImplemented

		if descendent.isAbsolute:
			raise ValueError('Cannot join path to absolute path')

		return Path(self._value, descendent._value)

	@property
	def parent(self):
		# os.path.dirname truncates the path at the last separator.
		# This is incorrect for paths like '../..' and '.'

		if self._value == os.path.normpath('.'):
			return Path('..')

		if self._value.endswith('..'):
			return Path(self._value, '..')

		# If os.path.dirname thinks this path points to the root
		parentPath = os.path.dirname(self._value)
		if self._value == parentPath:
			return None # no parent

		return Path(parentPath)

	def toAbsolute(self, context=None):
		context = context or os.getcwd()

		if self.isAbsolute:
			return self

		if not isinstance(context, Path):
			context = Path(context)

		if not context.isAbsolute:
			raise ValueError('Context path must be absolute')

		return context + self

	def relativeTo(self, ancestor):
		if isinstance(ancestor, basestring):
			ancestor = Path(ancestor)

		if not isinstance(ancestor, Path):
			raise TypeError('Expected path but found ' + type(ancestor).__name__)

		if self.isAbsolute != ancestor.isAbsolute:
			raise ValueError('Cannot compare absolute and relative paths.')

		return Path(os.path.relpath(self._value, ancestor._value))

	def exists(self):
		return os.path.exists(str(self))

	def existsAsFile(self):
		return os.path.isfile(str(self))

	def existsAsDirectory(self):
		return os.path.isdir(str(self))

	# TODO Add mode argument
	def makeDirectory(self, ancestors=True, failOnExist=False):
		if ancestors:
			# Build list of missing ancestors
			ancestorsToCreate = []
			curAncestor = self.toAbsolute().parent
			while curAncestor:
				if curAncestor.exists():
					break

				# Insert at front
				ancestorsToCreate.insert(0, curAncestor)

				# Continue up tree
				curAncestor = curAncestor.parent

			# Create missing ancestors
			for ancestor in ancestorsToCreate:
				# Could only exist due to race conditions, so ignore failures
				ancestor.makeDirectory(ancestors=False, failOnExist=False)

			# Create this directory
			self.makeDirectory(ancestors=False, failOnExist=failOnExist)
		else:
			try:
				# Try to create
				os.mkdir(str(self))
			except OSError as err:
				# Ignore if the directory already exists and failOnExist is False
				if err.errno == errno.EEXIST and os.path.isdir(str(self)):
					if failOnExist:
						raise
					else:
						return

				raise

	def find(self):
		if self.existsAsFile():
			yield self
		elif self.existsAsDirectory():
			for dirPath, subdirNames, fileNames in os.walk(str(self)):
				yield Path(dirPath)

				for fileName in fileNames:
					yield Path(dirPath, fileName)
		else:
			raise OSError('No such file or directory: ' + repr(str(self)))
