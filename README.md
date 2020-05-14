# wfc_python
An implementation of [mxgmn/WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse) in Python

WaveFunctionCollapse is an algorithm that generates bitmaps that are locally similar to the input bitmap. This is a translation into Python, based on the original implementation in C#.

This implementation has only had minimal testing and optimization (for example, it uses arrays of ints in places where the original C# code uses bytes). It can probably be sped up quite a lot. I can't promise I'll fix any issues any time soon, but if you run into anything please go ahead and report an issue (or submit a pull-request)!

An updated, re-implmented version of WaveFunctionCollapse in Python can be foudn at [ikarth/wfc_2019f](https://github.com/ikarth/wfc_2019f).
