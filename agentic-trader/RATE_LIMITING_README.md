# Rate Limiting Solution for KiteConnect API

## Overview

This solution addresses the "Too many requests" error from KiteConnect by implementing intelligent rate limiting, retry logic, and error handling.

## Features

### 1. **Rate Limiting**

- **API_DELAY**: 1 second delay between consecutive API calls
- **MAX_RETRIES**: 3 attempts for failed API calls
- **RETRY_DELAY**: 5 second wait before retrying after rate limit errors

### 2. **Smart Retry Logic**

- Automatically detects rate limit errors
- Implements exponential backoff for retries
- Continues processing even if some API calls fail

### 3. **Comprehensive Error Handling**

- Catches and logs all API errors
- Gracefully handles network failures
- Provides detailed logging for debugging

## Configuration

All settings are centralized in `config.py`:

```python
# API Rate Limiting Settings
API_DELAY = 1.0          # Delay between API calls in seconds
MAX_RETRIES = 3          # Maximum retries for failed calls
RETRY_DELAY = 5.0        # Delay before retrying after rate limit

# KiteConnect Settings
EXCHANGE = "NSE"
DEFAULT_CAPITAL = 15000

# Data Fetching Settings
HISTORICAL_INTERVAL = '5minute'
HISTORICAL_DURATION = '5d'
TOP_VOLUME_SIZE = 50
```

## Usage

### Basic Rate Limited API Call

```python
from test_strategies import safe_api_call, fetch_top_volume

# This will automatically handle rate limiting and retries
result = safe_api_call(fetch_top_volume, index_nifty='', size=10)
```

### Historical Data with Rate Limiting

```python
from benchmark import safe_fetch_historical

# Fetches historical data with automatic rate limiting
data = safe_fetch_historical("RELIANCE", interval='5minute', duration='5d')
```

## Implementation Details

### 1. **safe_api_call() Function**

- Wraps any API function with rate limiting
- Implements retry logic for rate limit errors
- Adds delays between calls automatically

### 2. **safe_fetch_historical() Function**

- Specifically designed for historical data fetching
- Handles KiteConnect-specific rate limit errors
- Provides detailed logging for each symbol

### 3. **Enhanced Logging**

- Structured logging with timestamps
- Progress tracking for long-running operations
- Error reporting with context

## Best Practices

### 1. **Adjust Rate Limits**

If you still hit rate limits, increase the delays:

```python
# In config.py
API_DELAY = 2.0        # Increase to 2 seconds
RETRY_DELAY = 10.0     # Increase to 10 seconds
```

### 2. **Batch Operations**

Group related API calls together to minimize delays:

```python
# Fetch all indices first
indices = ['', 'next', 'midcap', 'smallcap']
for index in indices:
    data = safe_api_call(fetch_top_volume, index_nifty=index, size=50)
    # Process data here
```

### 3. **Monitor Logs**

Watch the logs to understand API usage patterns:

```bash
python test_rate_limiting.py
```

## Testing

Run the rate limiting test:

```bash
python test_rate_limiting.py
```

This will test:

- Single API calls
- Multiple sequential calls
- Rate limit handling
- Error recovery

## Troubleshooting

### Common Issues

1. **Still hitting rate limits**

   - Increase `API_DELAY` in config.py
   - Reduce the number of concurrent operations
   - Add longer delays between different types of calls

2. **Slow performance**

   - Decrease `API_DELAY` if your API limits allow
   - Optimize to fetch data in larger batches
   - Use parallel processing where possible

3. **Memory issues with large datasets**
   - Reduce `TOP_VOLUME_SIZE` in config.py
   - Process data in smaller chunks
   - Implement data streaming for very large datasets

## Monitoring and Alerts

The logging system provides:

- Real-time progress updates
- Error rate monitoring
- Performance metrics
- API usage statistics

## Future Enhancements

1. **Dynamic Rate Limiting**

   - Adjust delays based on API response times
   - Implement adaptive backoff strategies

2. **Parallel Processing**

   - Process multiple symbols concurrently
   - Implement worker pools for better throughput

3. **Caching**

   - Cache frequently accessed data
   - Implement TTL-based cache invalidation

4. **Metrics Dashboard**
   - Real-time API usage monitoring
   - Performance analytics
   - Rate limit violation alerts
