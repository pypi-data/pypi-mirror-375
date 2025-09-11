# Datetime Plots

- [Introduction](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/datetime.md#introduction)
- [Datetime Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/datetime.md#datetime-plot)
- [Candlestick Plot](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/datetime.md#candlestick-plot)

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide)

## Introduction

* Plotting dates or times simply requires passing a list of date-time string objects (such as `"01/01/2000"`, `"12:30:32"` or `"01/01/2000 12:30:32"`) to the plotting functions. 

* To control how `plotext_plus` interprets string as date-time objects use the `date_form()` method, where you can change its: 
  
  * `input_form` parameter to control the form of date-time strings inputted by the user,
  
  * `output_form` parameter to control the form of date-time strings outputted by `plotext_plus` (by default equal to `input_form`), including outputted axes date-time ticks.

* The date-time string forms are [the standard ones](https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes), with the `%` symbol removed for simplicity; eg: `d/m/Y` (by default), or `d/m/Y H:M:S`.

* If needed, most of the functions that follow allow to optionally set their input and output forms independently, with their correspondent parameters, overwriting the `date_form()` settings.

- To get today in `datetime` or string form use `today_datetime()` and `today_string()` respectively.

- To turn a `datetime` object into a string use `datetime_to_string()` or `datetimes_to_strings()` for a list instead. 

- To turn a string into a `datetime` object use `string_to_datetime()`.

- To turn a string to a numerical time-stamp use `string_to_time()` and `strings_to_time()` for a list of strings.

- The method `set_time0()` sets the origin of time to the string provided; this function is useful in `log` scale, in order to avoid *hitting* the 0 time-stamp.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Datetime Menu](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/datetime.md#datetime-plots)

## Datetime Plot

To plot dates and/or times use either `plt.scatter()` or `plt.plot()` functions directly. 

Here is an example, which requires the package `yfinance`:

```python
import yfinance as yf
import plotext_plus as plt

plt.date_form('d/m/Y')

start = plt.string_to_datetime('11/04/2022')
end = plt.today_datetime()
data = yf.download('goog', start, end)

prices = list(data["Close"])
dates = plt.datetimes_to_string(data.index)

plt.plot(dates, prices)

plt.title("Google Stock Price")
plt.xlabel("Date")
plt.ylabel("Stock Price $")
plt.show()
```

or directly on terminal:

```console
python3 -c "import yfinance as yf; import plotext_plus as plt; plt.date_form('d/m/Y'); start = plt.string_to_datetime('11/04/2022'); end = plt.today_datetime(); data = yf.download('goog', start, end); prices = list(data['Close']); dates = plt.datetimes_to_string(data.index); plt.plot(dates, prices); plt.title('Google Stock Price'); plt.xlabel('Date'); plt.ylabel('Stock Price $'); plt.show()"
```

![datetime](https://raw.githubusercontent.com/ccmitchellusa/plotext/master/data/datetime.png)

Note that you could easily add [text](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/decorator.md#text-plot) and [lines](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/decorator.md#plot-lines) to the plot, as date-time string coordinates are allowed in most plotting functions.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Datetime Menu](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/datetime.md#datetime-plots)

## Candlestick Plot

For this kind of plot, use the function `candlestick()`, which requires a list of date-time strings and a dictionary with the following `'Open'`, `'Close'`, `'High'`, and `'Low'` mandatory keys, and where each correspondent value is a list of prices. 

Here is an example, which requires the package `yfinance`:

```python
import yfinance as yf
import plotext_plus as plt

plt.date_form('d/m/Y')

start = plt.string_to_datetime('11/04/2022')
end = plt.today_datetime()
data = yf.download('goog', start, end)

dates = plt.datetimes_to_string(data.index)

plt.candlestick(dates, data)

plt.title("Google Stock Price CandleSticks")
plt.xlabel("Date")
plt.ylabel("Stock Price $")
plt.show()
```

or directly on terminal:

```bash
python3 -c "import yfinance as yf; import plotext_plus as plt; plt.date_form('d/m/Y'); start = plt.string_to_datetime('11/04/2022'); end = plt.today_datetime(); data = yf.download('goog', start, end); dates = plt.datetimes_to_string(data.index); plt.candlestick(dates, data); plt.title('Google Stock Price Candlesticks'); plt.xlabel('Date'); plt.ylabel('Stock Price $'); plt.show()"
```

![datetime](https://raw.githubusercontent.com/ccmitchellusa/plotext_plus/master/data/candlestick.png)

More documentation can be accessed with `doc.candlestick()`.

[Main Guide](https://github.com/ccmitchellusa/plotext_plus#guide), [Datetime Menu](https://github.com/ccmitchellusa/plotext_plus/blob/master/docs/datetime.md#datetime-plots)
