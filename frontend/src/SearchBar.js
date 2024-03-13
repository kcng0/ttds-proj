import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  InputGroup,
  FormControl,
  Button,
} from "react-bootstrap";
import { BsSearch } from "react-icons/bs";
import BASE_URL from "./api";
import debounce from "lodash.debounce";

function SearchBar() {
  const [searchQuery, setSearchQuery] = useState("");
  const [searchType, setSearchType] = useState("tfidf");
  const [errorMessage, setErrorMessage] = useState("");
  const [suggestions, setSuggestions] = useState([]);

  const handleSearchClick = async () => {
    setErrorMessage("");
    if (!searchQuery.trim()) {
      setErrorMessage("Please enter a search query.");
      return;
    }

    // navigate the search page with url: /search?q=searchQuery.trim()&type=searchType&limit=10&page=1
    let params = new URLSearchParams();
    params.append("q", encodeURIComponent(searchQuery.trim()));
    params.append("type", searchType);
    params.append("limit", 10);
    params.append("page", 1);
    window.location.href = `/search?${params.toString()}`;
  };
  const fetchSuggestions = async (query) => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    try {
      const response = await fetch(`${BASE_URL}/search/expand-query/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ query: query, num_expansions: 5 }), // Adjust num_expansions as needed
      });
      const data = await response.json();
      setSuggestions(data.expanded_queries);
    } catch (error) {
      console.error("Error fetching query suggestions:", error);
      setSuggestions([]);
    }
  };
  
  const debouncedFetchSuggestions = debounce(fetchSuggestions, 300);
  const handleChange = (e) => {
    const query = e.target.value;
    setSearchQuery(query);
    debouncedFetchSuggestions(query);
  };
  // --> clean up the debounced function on unmount
  useEffect(() => {
    return () => {
      debouncedFetchSuggestions.cancel();
    };
  }, []);

  return (
    <>
      {errorMessage && (
        <div style={{ color: "red", marginBottom: "10px" }}>{errorMessage}</div>
      )}{" "}
      {/* Display error message here */}
      <InputGroup className="mb-3">
        <FormControl
          placeholder="Search"
          aria-label="Search"
          value={searchQuery}
          onChange={handleChange} // Updated to use the new handleChange function                            spellCheck="true" // Enable spell check here
          autoComplete="on" // Enabled autocomplete here
          autoCorrect="on" // Enabled auto correct here
        />
        <select
          className="form-select"
          value={searchType}
          onChange={(e) => setSearchType(e.target.value)}
          style={{ maxWidth: "120px" }}
        >
          {/* <option value="standard">Standard</option> */}
          <option value="tfidf">TF-IDF</option>
          <option value="boolean">Boolean</option>
        </select>
        <Button variant="outline-secondary" onClick={handleSearchClick}>
          <BsSearch />
        </Button>
      </InputGroup>
      {suggestions.length > 0 && (
        <ul className="list-group">
          {suggestions.map((suggestion, index) => (
            <li
              key={index}
              className="list-group-item list-group-item-action"
              onClick={() => {
                setSearchQuery(suggestion);
                setSuggestions([]); // Clear suggestions after selection
              }}
            >
              {suggestion}
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

export default SearchBar;
