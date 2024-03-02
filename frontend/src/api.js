
const BASE_URL = 'http://localhost:8080'; // Update with your backend URL

export const fetchSearchResults = async (query, year, page = 1, limit = 10) => {
    // Remove empty parameters from the request
    const params = new URLSearchParams();
    params.append('q', query);
    if (year) params.append('year', year);
    if (page) params.append('page', page);
    if (limit) params.append('limit', limit);

    const url = `${BASE_URL}/search?${params.toString()}`;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch search results');
        }
        return await response.json();
    } catch (error) {
        console.error('Error fetching search results:', error);
        throw error;
    }
};


export const postSearchTest = async (data) => {
    try {
        const response = await fetch(`${BASE_URL}/search/test`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error('Failed to post search test');
        }
        return await response.json();
    } catch (error) {
        console.error('Error posting search test:', error);
        throw error;
    }
};

export const fetchSearchBoolean = async (query, page = 1, limit = 10) => {
    try {
      const url = `${BASE_URL}/search/boolean?q=${encodeURIComponent(query)}&page=${page}&limit=${limit}`;
      const response = await fetch(url, {
        headers: {
          'Accept': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok (status: ${response.status})`);
      }
      const data = await response.json();
      return data.results; // Assuming your API wraps the results in a "results" key
    } catch (error) {
      console.error('There was a problem fetching the boolean search results:', error);
      throw error;
    }
  };

export const fetchSearchTfidf = async (query, page = 1, limit = 10) => {
    try {
      // Ensure BASE_URL is defined somewhere in your api.js, e.g., const BASE_URL = 'http://127.0.0.1:8000';
      const url = `${BASE_URL}/search/tfidf?q=${encodeURIComponent(query)}&page=${page}&limit=${limit}`;
      const response = await fetch(url, {
        headers: {
          'accept': 'application/json'
        }
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok (status: ${response.status})`);
      }
      const data = await response.json();
      return data.results; // You might need to adjust this depending on the shape of your API response.
    } catch (error) {
      console.error('There was a problem fetching the TF-IDF search results:', error);
      throw error; // Re-throw the error so it can be caught and handled by the caller.
    }
};

