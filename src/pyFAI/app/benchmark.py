#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Project: Fast Azimuthal integration
#             https://github.com/silx-kit/pyFAI
#
#
#    Copyright (C) 2012-2023 European Synchrotron Radiation Facility, Grenoble, France
#
#    Authors: Jérôme Kieffer <Jerome.Kieffer@ESRF.eu>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#  .
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#  .
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

"""utility to run the benchmark for azimuthal integration on images of various sizes"""
__author__ = "Jérôme Kieffer, Picca Frédéric-Emmanuel, Edgar Gutierrez-Fernandez"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20/12/2023"
__status__ = "development"

import logging
try:
    logging.basicConfig(level=logging.WARNING, force=True)
except ValueError:
    logging.basicConfig(level=logging.WARNING)
logging.captureWarnings(True)
logger = logging.getLogger(__name__)
try:
    import hdf5plugin  # noqa
except ImportError:
    logger.debug("Unable to load hdf5plugin, backtrace:", exc_info=True)

try:
    from rfoo.utils import rconsole
    rconsole.spawn_server()
except ImportError:
    logger.debug("No socket opened for debugging. Please install rfoo")
import pyFAI.benchmark


def main():
    from argparse import ArgumentParser
    description = """Benchmark for Azimuthal integration
    """
    epilog = """  """
    usage = """benchmark [options] """
    version = "pyFAI benchmark version " + pyFAI.version
    parser = ArgumentParser(usage=usage, description=description, epilog=epilog)
    parser.add_argument("-v", "--version", action='version', version=version)
    parser.add_argument("-d", "--debug",
                        action="store_true", dest="debug", default=False,
                        help="switch to verbose/debug mode")
    parser.add_argument("--no-proc",
                        action="store_false", dest="processor", default=True,
                        help="do not benchmark using the central processor")
    parser.add_argument("-c", "--cpu",
                        action="store_true", dest="opencl_cpu", default=False,
                        help="perform benchmark using OpenCL on the CPU")
    parser.add_argument("-g", "--gpu",
                        action="store_true", dest="opencl_gpu", default=False,
                        help="perform benchmark using OpenCL on the GPU")
    parser.add_argument("-a", "--acc",
                        action="store_true", dest="opencl_acc", default=False,
                        help="perform benchmark using OpenCL on the Accelerator (like XeonPhi/MIC)")
    parser.add_argument("-s", "--size", type=float,
                        dest="size", default=1000,
                        help="Limit the size of the dataset to X Mpixel images (for computer with limited memory)")
    parser.add_argument("-n", "--number",
                        dest="number", default=10, type=float,
                        help="Perform the test for this amount of time, by default 10s/measurment")
    parser.add_argument("-2d", "--2dimention",
                        action="store_true", dest="twodim", default=False,
                        help="Benchmark also algorithm for 2D-regrouping")
    parser.add_argument("--no-1dimention",
                        action="store_false", dest="onedim", default=True,
                        help="Do not benchmark algorithms for 1D-regrouping")

    parser.add_argument("-m", "--memprof",
                        action="store_true", dest="memprof", default=False,
                        help="Perfrom memory profiling (Linux only)")
    parser.add_argument("-r", "--repeat",
                        dest="repeat", default=1, type=int,
                        help="Repeat each measurement x times to take the best")
    
    parser.add_argument("-ps", "--pixelsplit",
                        dest="pixelsplit", default=["bbox"], type=str, nargs="+",
                        help="Benchmark using specific pixel splitting protocols: no, bbox, pseudo, full",)
    parser.add_argument("-algo", "--algorithm",
                        dest="algorithm", default=["histogram", "CSR"], type=str, nargs="+",
                        help="Benchmark using specific algorithms: histogram, CSR, CSC, all")
    parser.add_argument("-i", "--implementation",
                        dest="implementation", default=["cython", "opencl"], type=str, nargs="+",
                        help="Benchmark using specific algorithm implementations: python, cython, opencl, all")
    
    parser.add_argument("-f", "--function",
                        dest="function", default="all", type=str,
                        help="Benchmark legacy (legacy), engine function (ng), or both (all)")

    parser.add_argument("--all",
                        action="store_true", dest="all", default=False,
                        help="Benchmark using all available methods and devices")

    options = parser.parse_args()
    if options.debug:
        pyFAI.logger.setLevel(logging.DEBUG)

    devices = []
    if options.opencl_cpu:
        devices.append("cpu")
    if options.opencl_gpu:
        devices.append("gpu")
    if options.opencl_acc:
        devices.append("acc")
    
    pyFAI.benchmark.run(number=options.number,
                        repeat=options.repeat,
                        memprof=options.memprof,
                        max_size=options.size,
                        do_1d=options.onedim,
                        do_2d=options.twodim,
                        processor=options.processor,
                        devices=devices,
                        split_list=options.pixelsplit,
                        algo_list=options.algorithm,
                        impl_list=options.implementation,
                        function=options.function,
                        all=options.all,
                        )

    if pyFAI.benchmark.pylab is not None:
        pyFAI.benchmark.pylab.ion()
    input("Enter to quit")


if __name__ == "__main__":
    main()
