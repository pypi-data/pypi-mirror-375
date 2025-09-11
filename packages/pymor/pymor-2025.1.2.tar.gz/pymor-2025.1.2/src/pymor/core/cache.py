# This file is part of the pyMOR project (https://www.pymor.org).
# Copyright pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (https://opensource.org/licenses/BSD-2-Clause)

"""This module provides the caching facilities of pyMOR.

Any class that wishes to provide cached method calls should derive from
:class:`CacheableObject`. Methods which are to be cached can then
be marked using the :class:`cached` decorator.

To ensure consistency, :class:`CacheableObject` derives from
|ImmutableObject|: The return value of a cached method call should
only depend on its arguments as well as the immutable state of the class
instance.

Making this assumption, the keys for cache lookup are created from
the following data:

    1. the instance's :attr:`~CacheableObject.cache_id` in case of a
       :attr:`~CacheRegion.persistent` :class:`CacheRegion`, else the instance's
       :attr:`~pymor.core.base.BasicObject.uid`,
    2. the method's `__name__`,
    3. the method's arguments.

Note that instances of |ImmutableObject| are allowed to have mutable
private attributes. It is the implementer's responsibility not to break things.
(See this :ref:`warning <ImmutableObjectWarning>`.)

Backends for storage of cached return values derive from :class:`CacheRegion`.
Currently two backends are provided for memory-based and disk-based caching
(:class:`MemoryRegion` and :class:`DiskRegion`). The available regions
are stored in the module level `cache_regions` dict. The user can add
additional regions (e.g. multiple disk cache regions) as required.
:attr:`CacheableObject.cache_region` specifies a key of the `cache_regions` dict
to select a cache region which should be used by the instance.
(Setting :attr:`~CacheableObject.cache_region` to `None` or `'none'` disables caching.)

By default, a 'memory', a 'disk' and a 'persistent' cache region are configured. The
paths and maximum sizes of the disk regions, as well as the maximum number of keys of
the memory cache region can be configured via the
`pymor.core.cache.default_regions.disk_path`,
`pymor.core.cache.default_regions.disk_max_size`,
`pymor.core.cache.default_regions.persistent_path`,
`pymor.core.cache.default_regions.persistent_max_size` and
`pymor.core.cache.default_regions.memory_max_keys` |defaults|.

There two ways to disable and enable caching in pyMOR:

    1. Calling :func:`disable_caching` (:func:`enable_caching`), to disable
       (enable) caching globally.
    2. Calling :meth:`CacheableObject.disable_caching`
       (:meth:`CacheableObject.enable_caching`) to disable (enable) caching
       for a given instance.

Caching of a method is only active if caching has been enabled both globally
(enabled by default) and on instance level. For debugging purposes, it is moreover
possible to set the environment variable `PYMOR_CACHE_DISABLE=1` which overrides
any call to :func:`enable_caching`.

A cache region can be emptied using :meth:`CacheRegion.clear`. The function
:func:`clear_caches` clears each cache region registered in `cache_regions`.
"""

import atexit
import functools
import getpass
import hashlib
import inspect
import os
import tempfile
from collections import OrderedDict, defaultdict
from copy import deepcopy
from numbers import Number
from textwrap import wrap
from types import MethodType

import diskcache
import numpy as np

from pymor.core.base import ImmutableObject
from pymor.core.defaults import defaults, defaults_changes
from pymor.core.exceptions import CacheKeyGenerationError, UnpicklableError
from pymor.core.logger import getLogger
from pymor.core.pickle import dumps
from pymor.parameters.base import Mu
from pymor.tools.frozendict import FrozenDict


@atexit.register
def cleanup_non_persistent_regions():
    for region in cache_regions.values():
        if not region.persistent:
            region.clear()


def _safe_filename(old_name):
    return ''.join(x for x in old_name if (x.isalnum() or x in '._- '))


class CacheRegion:
    """Base class for all pyMOR cache regions.

    Attributes
    ----------
    persistent
        If `True`, cache entries are kept between multiple
        program runs.
    """

    persistent = False

    def get(self, key):
        """Return cache entry for given key.

        Parameters
        ----------
        key
            The key for the cache entry.

        Returns
        -------
        `(True, entry)`
            in case the `key` has been found in the cache region.
        `(False, None)`
            in case the `key` is not present in the cache region.
        """
        raise NotImplementedError

    def set(self, key, value):
        """Set cache entry for `key` to given `value`.

        This method is usually called only once for
        any given `key` (with the exemption of issues
        due to concurrency).
        """
        raise NotImplementedError

    def clear(self):
        """Clear the entire cache region."""
        raise NotImplementedError


class MemoryRegion(CacheRegion):

    NO_VALUE = {}  # noqa: RUF012

    def __init__(self, max_keys):
        self.max_keys = max_keys
        self._cache = OrderedDict()

    def get(self, key):
        value = self._cache.get(key, self.NO_VALUE)
        if value is self.NO_VALUE:
            return False, None
        else:
            return True, deepcopy(value)

    def set(self, key, value):
        if key in self._cache:
            getLogger('pymor.core.cache.MemoryRegion').warning('Key already present in cache region, ignoring.')
            return
        if len(self._cache) == self.max_keys:
            self._cache.popitem(last=False)
        self._cache[key] = deepcopy(value)

    def clear(self):
        self._cache = OrderedDict()


class DiskRegion(CacheRegion):

    def __init__(self, path, max_size, persistent):
        self.path = path
        self.max_size = max_size
        self.persistent = persistent
        self._cache = diskcache.Cache(path)
        self._cache.reset('size_limit', int(max_size))

        if not persistent:
            self.clear()

    def get(self, key):
        has_key = key in self._cache
        return has_key, self._cache.get(key, default=None)

    def set(self, key, value):
        has_key = key in self._cache
        if has_key:
            getLogger('pymor.core.cache.DiskRegion').warning('Key already present in cache region, ignoring.')
            return
        try:
            self._cache.set(key, value)
        except UnpicklableError as e:
            getLogger('pymor.core.cache.DiskRegion').warning(f'{e.cls} cannot be pickled. Not caching result.')
        except (TypeError, AttributeError) as e:
            getLogger('pymor.core.cache.DiskRegion').warning(f'Pickling failed. Not caching result (error: {e}).')

    def clear(self):
        self._cache.clear()


@defaults('disk_path', 'disk_max_size', 'persistent_path', 'persistent_max_size', 'memory_max_keys')
def default_regions(disk_path=os.path.join(tempfile.gettempdir(), 'pymor.cache.' + getpass.getuser()),
                    disk_max_size=1024 ** 3,
                    persistent_path=os.path.join(tempfile.gettempdir(), 'pymor.persistent.cache.' + getpass.getuser()),
                    persistent_max_size=1024 ** 3,
                    memory_max_keys=1000):

    parse_size_string = lambda size: \
        int(size[:-1]) * 1024 if size[-1] == 'K' else \
        int(size[:-1]) * 1024 ** 2 if size[-1] == 'M' else \
        int(size[:-1]) * 1024 ** 3 if size[-1] == 'G' else \
        int(size)

    if isinstance(disk_max_size, str):
        disk_max_size = parse_size_string(disk_max_size)

    cache_regions['disk'] = DiskRegion(path=disk_path, max_size=disk_max_size, persistent=False)
    cache_regions['persistent'] = DiskRegion(path=persistent_path, max_size=persistent_max_size, persistent=True)
    cache_regions['memory'] = MemoryRegion(memory_max_keys)


cache_regions = {}

_caching_disabled = int(os.environ.get('PYMOR_CACHE_DISABLE', 0)) == 1
if _caching_disabled:
    getLogger('pymor.core.cache').warning('caching globally disabled by environment')


def enable_caching():
    """Globally enable caching."""
    global _caching_disabled
    _caching_disabled = int(os.environ.get('PYMOR_CACHE_DISABLE', 0)) == 1


def disable_caching():
    """Globally disable caching."""
    global _caching_disabled
    _caching_disabled = True


def clear_caches():
    """Clear all cache regions."""
    for r in cache_regions.values():
        r.clear()


class CacheableObject(ImmutableObject):
    """Base class for anything that wants to use our built-in caching.

    Attributes
    ----------
    cache_region
        Name of the :class:`CacheRegion` to use. Must correspond to a key in
        the :attr:`cache_regions` dict. If `None` or `'none'`, caching
        is disabled.
    cache_id
        Identifier for the object instance on which a cached method is called.
    """

    cache_region = None
    cache_id = None

    def disable_caching(self):
        """Disable caching for this instance."""
        self.__dict__['cache_region'] = None
        self.__dict__['cache_id'] = None

    def enable_caching(self, region, cache_id=None):
        """Enable caching for this instance.

        .. warning::
            Note that using :meth:`~pymor.core.base.ImmutableObject.with_`
            will reset :attr:`cache_region` and :attr:`cache_id` to their class
            defaults.

        Parameters
        ----------
        region
            Name of the |CacheRegion| to use. Must correspond to a key in
            the :attr:`cache_regions` dict. If `None` or `'none'`, caching
            is disabled.
        cache_id
            Identifier for the object instance on which a cached method is called.
            Must be specified when `region` is :attr:`~CacheRegion.persistent`.
            When `region` is not :attr:`~CacheRegion.persistent` and no `cache_id`
            is given, the object's :attr:`~pymor.core.base.BasicObject.uid`
            is used instead.
        """
        self.__dict__['cache_id'] = cache_id
        if region in (None, 'none'):
            self.__dict__['cache_region'] = None
        else:
            self.__dict__['cache_region'] = region
            r = cache_regions.get(region)
            if r and r.persistent and cache_id is None:
                raise ValueError('For persistent CacheRegions a cache_id has to be specified.')

    def _get_cache_region_and_key(self, key_data):
        if not cache_regions:
            default_regions()
        try:
            region = cache_regions[self.cache_region]
        except KeyError as e:
            raise ValueError(f'No cache region "{self.cache_region}" found') from e

        # id for self
        assert self.cache_id or not region.persistent
        self_id = self.cache_id or self.uid

        cache_key = build_cache_key((self_id, key_data))

        return region, cache_key

    def get_cached_value(self, key_data, value_factory=None):
        """Retrieve value from cache.

        This low-level method allows retrieving cached values for pairs
        `(self, key_data)` from the object's active |CacheRegion|.

        If the corresponding value is not found in the cache, `value_factory`
        is called to compute the value. The value is then stored in the
        |CacheRegion| and returned. If `value_factory` is `None`, a `KeyError`
        is raised.

        In most cases, the :func:`cached` decorator should be used instead.

        Parameters
        ----------
        key_data
            The data/parameters from which the cache key is computed that is
            used to retrieve the value.
        value_factory
            A callable with no parameters that computes the desired value
            in case of a cache miss.

        Returns
        -------
        The cached value corresponding to the pair `(self, key)`.
        """
        if _caching_disabled or self.cache_region is None:
            raise KeyError(key_data)

        region, cache_key = self._get_cache_region_and_key(key_data)

        found, value = region.get(cache_key)

        if not found:
            if value_factory is not None:
                value = value_factory()
                region.set(cache_key, (value, defaults_changes()))
                return value
            else:
                raise KeyError(key_data)

        value, cached_defaults_changes = value
        if cached_defaults_changes != defaults_changes():
            getLogger('pymor.core.cache').warning('pyMOR defaults have been changed. Cached result may be wrong.')

        return value

    def set_cached_value(self, key_data, value):
        """Store value in active |CacheRegion|.

        This low-level method allows storing values for pairs `(self, key)`
        in the object's active |CacheRegion| for later retrieval.

        In most cases, the :func:`cached` decorator should be used instead.

        Parameters
        ----------
        key_data
            The data/parameters from which the cache key is computed that is
            used to store the value.
        value
            Value to be stored.
        """
        if _caching_disabled or self.cache_region is None:
            return

        region, cache_key = self._get_cache_region_and_key(key_data)
        region.set(cache_key, (value, defaults_changes()))

    def cached_method_call(self, method, *args, **kwargs):
        """Call a given `method` and cache the return value.

        This method can be used as an alternative to the :func:`cached`
        decorator.

        Parameters
        ----------
        method
            The method that is to be called. This has to be a method
            of `self`.
        args
            Positional arguments for `method`.
        kwargs
            Keyword arguments for `method`

        Returns
        -------
        The (possibly cached) return value of `method(*args, **kwargs)`.
        """
        assert isinstance(method, MethodType)

        # shortcut to avoid key generation when caching is disabled
        if _caching_disabled or self.cache_region is None:
            return method(*args, **kwargs)

        params = inspect.signature(method).parameters
        if any(v.kind == v.VAR_POSITIONAL for v in params.values()):
            raise NotImplementedError
        argnames = list(params.keys())[1:]  # first argument is self
        defaults = {k: v.default for k, v in params.items() if v.default is not v.empty}
        return self._cached_method_call(method, False, argnames, defaults, args, kwargs)

    def _cached_method_call(self, method, pass_self, argnames, defaults, args, kwargs):
        # ensure that passing a value as positional or keyword argument does not matter
        kwargs.update(zip(argnames, args))

        # ensure the values of optional parameters enter the cache key
        if defaults:
            kwargs = dict(defaults, **kwargs)

        # assume that all parameters named mu expect parameter values
        # in case the value is not a Mu instance parse it to avoid cache misses
        if 'mu' in kwargs and not isinstance(kwargs['mu'], Mu):
            kwargs['mu'] = self.parameters.parse(kwargs['mu'])

        def value_factory():
            self.logger.debug(f'creating new cache entry for {self.__class__.__name__}.{method.__name__}')
            return method(self, **kwargs) if pass_self else method(**kwargs)

        return self.get_cached_value((method.__name__, kwargs), value_factory)


_CACHED_METHODS = []


def cached(function):
    """Decorator to make a method of `CacheableObject` actually cached."""
    params = inspect.signature(function).parameters
    if any(v.kind == v.VAR_POSITIONAL for v in params.values()):
        raise NotImplementedError
    argnames = list(params.keys())[1:]  # first argument is self
    defaults = {k: v.default for k, v in params.items() if v.default is not v.empty}

    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        if _caching_disabled or self.cache_region is None:
            return function(self, *args, **kwargs)
        return self._cached_method_call(function, True, argnames, defaults, args, kwargs)

    _CACHED_METHODS.append(function.__qualname__)

    return wrapper


def print_cached_methods():
    from pymor.core.defaults import _import_all
    _import_all()

    print(f"""
Overview of cached methods
--------------------------

Caching is globally {"disabled" if _caching_disabled else "enabled"}.

Use enable_caching()/disable_caching() to globally enable/disable caching.
To enable/disable caching for a single CacheableObject, use its individual
enable_caching()/disable_caching() methods.

The following methods are cached when caching is enabled both globally
and on a per-instance level:
"""[1:])

    print(*wrap(', '.join(sorted(_CACHED_METHODS)), initial_indent='  ', subsequent_indent='  '), sep='\n')

    # get all classes of CacheableObjects
    cacheable_classes = []
    def add_subclasses(parent):
        for c in parent.__subclasses__():
            cacheable_classes.append(c)
            add_subclasses(c)
    add_subclasses(CacheableObject)

    regions_with_classes = defaultdict(list)
    for c in cacheable_classes:
        if c.cache_region is not None:
            regions_with_classes[c.cache_region].append(c.__qualname__)

    print('\n\nThe following classes have caching enabled by default:\n')

    for region, classes in sorted(regions_with_classes.items(), key=lambda x: x[0]):
        print(f'Default cache region: {region}\n')
        print(*wrap(', '.join(sorted(classes)), initial_indent='  ', subsequent_indent='  '), sep='\n')
        print()
        print()

    print("""
Note that cacheable classes outside the pymor package are only listed
when the modules containing these classes have already been imported.
"""[1:])


NoneType = type(None)


def build_cache_key(obj):

    def transform_obj(obj):
        t = type(obj)
        if hasattr(obj, '_cache_key_reduce'):
            return transform_obj(obj._cache_key_reduce())
        elif t in (NoneType, bool, int, float, str, bytes):
            return obj
        elif t is np.ndarray:
            if obj.dtype == object:
                raise CacheKeyGenerationError('Cannot generate cache key for provided arguments')
            # we need to upcast into the largest possible dtype, to ensure portable hashing
            # e.g., numpy < 2 uses int32 per default on Windows, but int64 everywhere else
            if np.issubdtype(obj.dtype, np.integer) or np.issubdtype(obj.dtype, np.floating):
                return obj.astype(np.float64)
            elif np.issubdtype(obj.dtype, np.complexfloating):
                return obj.astype(np.complex128)
            return obj
        elif t in (list, tuple):
            return tuple(transform_obj(o) for o in obj)
        elif t in (set, frozenset):
            return tuple(transform_obj(o) for o in sorted(obj))
        elif t in (dict, FrozenDict):
            return tuple((transform_obj(k), transform_obj(v)) for k, v in sorted(obj.items()))
        elif isinstance(obj, Number):
            # handle numpy number objects
            return obj
        else:
            raise CacheKeyGenerationError('Cannot generate cache key for provided arguments')

    obj = transform_obj(obj)
    key = hashlib.sha256(dumps(obj, protocol=-1)).hexdigest()

    return key
