#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import traceback
import mapnik
import pytest

READ_FLAGS = 'rb'
HERE = os.path.dirname(__file__)

def execution_path(filename):
    return os.path.join(os.path.dirname(
        sys._getframe(1).f_code.co_filename), filename)

def contains_word(word, bytestring_):
    """
    Checks that a bytestring contains a given word. len(bytestring) should be
    a multiple of len(word).

    >>> contains_word("abcd", "abcd"*5)
    True

    >>> contains_word("ab", "ba"*5)
    False

    >>> contains_word("ab", "ab"*5+"a")
    Traceback (most recent call last):
    ...
    AssertionError: len(bytestring_) not multiple of len(word)
    """
    n = len(word)
    assert len(bytestring_) % n == 0, "len(bytestring_) not multiple of len(word)"
    chunks = [bytestring_[i:i + n] for i in range(0, len(bytestring_), n)]
    return word in chunks


def pixel2channels(pixel):
    alpha = (pixel >> 24) & 0xff
    red = pixel & 0xff
    green = (pixel >> 8) & 0xff
    blue = (pixel >> 16) & 0xff
    return red, green, blue, alpha


def pixel2rgba(pixel):
    return 'rgba(%s,%s,%s,%s)' % pixel2channels(pixel)


def get_unique_colors(im):
    pixels = []
    for x in range(im.width()):
        for y in range(im.height()):
            pixel = im.get_pixel(x, y)
            if pixel not in pixels:
                pixels.append(pixel)
    pixels = sorted(pixels)
    return list(map(pixel2rgba, pixels))

def side_by_side_image(left_im, right_im):
    width = left_im.width() + 1 + right_im.width()
    height = max(left_im.height(), right_im.height())
    im = mapnik.Image(width, height)
    im.composite(left_im, mapnik.CompositeOp.src_over, 1.0, 0, 0)
    if width > 80:
        im.composite(
            mapnik.Image.open(
                HERE +
                '/images/expected.png'),
            mapnik.CompositeOp.difference,
            1.0,
            0,
            0)
    im.composite(
        right_im,
        mapnik.CompositeOp.src_over,
        1.0,
        left_im.width() + 1,
        0)
    if width > 80:
        im.composite(
            mapnik.Image.open(
                HERE +
                '/images/actual.png'),
            mapnik.CompositeOp.difference,
            1.0,
            left_im.width() +
            1,
            0)
    return im


def assert_box2d_almost_equal(a, b, msg=None):
    msg = msg or ("%r != %r" % (a, b))
    assert a.minx == pytest.approx(b.minx, abs=1e-2), msg
    assert a.maxx == pytest.approx(b.maxx, abs=1e-2), msg
    assert a.miny == pytest.approx(b.miny, abs=1e-2), msg
    assert a.maxy == pytest.approx(b.maxy, abs=1e-2), msg


def images_almost_equal(image1, image2, tolerance = 1):
    def rgba(p):
        return p & 0xff,(p >> 8) & 0xff,(p >> 16) & 0xff, p >> 24
    assert image1.width()  == image2.width()
    assert image1.height() == image2.height()
    for x in range(image1.width()):
        for y in range(image1.height()):
            p1 = image1.get_pixel(x, y)
            p2 = image2.get_pixel(x, y)
            assert rgba(p1) == pytest.approx(rgba(p2), abs = tolerance)
