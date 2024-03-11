import React, { useState,useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { Container, InputGroup, FormControl, Button, Navbar, Nav } from 'react-bootstrap';
import { BsSearch } from 'react-icons/bs';
import StandardResultsPage from './StandardResultsPage'; 
import BooleanResultsPage from './BooleanResultsPage';
import TfidfResultsPage from './TfidfResultsPage';
import ErrorPage from './ErrorPage';
import HowItWorks from './HowItWorks';
import { fetchSearchResults, fetchSearchBoolean, fetchSearchTfidf } from './api';
import logoImage from './logo.png';
import debounce from 'lodash.debounce';

function App() {
    const [searchQuery, setSearchQuery] = useState('');
    const [searchResults, setSearchResults] = useState([]);
    const [searchType, setSearchType] = useState('tfidf'); // 'standard' or 'boolean'
    const [errorMessage, setErrorMessage] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    let navigate = useNavigate();

    const handleSearchClick = async () => {
        setErrorMessage('');
        if (!searchQuery.trim()) {
            setErrorMessage('Please enter a search query.');
            return;
        }
      
        try {
          let results;
          console.log("SearchType:");
          console.log(searchType);
          if (searchType === 'standard') {
            results = await fetchSearchResults(searchQuery.trim());
            navigate('/StandardResultsPage', { state: { searchResults: results, searchType: 'standard' } });
          } else if (searchType === 'boolean') {
            results = await fetchSearchBoolean(searchQuery.trim());
            // Include the search query as a URL parameter
            navigate(`/BooleanResultsPage?q=${encodeURIComponent(searchQuery.trim())}`, { state: { searchResults: results, searchType: 'boolean' } });
          } else if (searchType === 'tfidf') { // Handle TF-IDF search
            results = await fetchSearchTfidf(searchQuery.trim());
            navigate(`/TfidfResultsPage?q=${encodeURIComponent(searchQuery.trim())}`, { state: { searchResults: results, searchType: 'tfidf' } });
          }
        } catch (error) {
            console.error(`Error fetching ${searchType} search results:`, error);
            navigate('/error'); // Redirect to the error page
        }
      };
      const fetchSuggestions = async (query) => {
        if (!query.trim()) {
          setSuggestions([]);
          return;
        }
      
        try {
          const response = await fetch(`http://127.0.0.1:8080/search/expand-query/`, { 
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ query: query, num_expansions: 5 }), // Adjust num_expansions as needed
          });
          const data = await response.json();
          setSuggestions(data.expanded_queries);
        } catch (error) {
          console.error('Error fetching query suggestions:', error);
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
            <Navbar bg="light" expand="lg">
                <Container>
                    <Navbar.Brand as={Link} to="/">FactChecker</Navbar.Brand>
                    <Navbar.Toggle aria-controls="basic-navbar-nav" />
                    <Navbar.Collapse id="basic-navbar-nav">
                        <Nav className="me-auto">
                            <Nav.Link as={Link} to="/">Home</Nav.Link>
                            <Nav.Link as={Link} to="/how-it-works">How It Works</Nav.Link>
                        </Nav>
                    </Navbar.Collapse>
                </Container>
            </Navbar>

            <Container className="d-flex flex-column justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
                <div className="text-center">
                    <img 
                        src={logoImage} 
                        alt="FactChecker Logo" 
                        style={{ maxWidth: '350px', width: '100%', marginBottom: '20px' }}
                    />
                    {errorMessage && <div style={{ color: 'red', marginBottom: '10px' }}>{errorMessage}</div>} {/* Display error message here */}
                        <InputGroup className="mb-3">
                        <FormControl
                            placeholder="Search"
                            aria-label="Search"
                            value={searchQuery}
                            onChange={handleChange} // Updated to use the new handleChange function                            spellCheck="true" // Enable spell check here
                            autoComplete='on' // Enabled autocomplete here
                            autoCorrect='on' // Enabled auto correct here
                            
                        />
                        <select
                            className="form-select"
                            value={searchType}
                            onChange={(e) => setSearchType(e.target.value)}
                            style={{ maxWidth: '120px' }}
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
                </div>
            </Container>

            <footer className="text-center bg-light py-3">
                <Container>
                    © {new Date().getFullYear()} FactChecker - All Rights Reserved
                    <div>
                        <a href="#privacy-policy">Privacy Policy</a> | <a href="#terms-of-service">Terms of Service</a>
                    </div>
                    <div>
                        Follow us: 
                        <a href="#twitter" className="ms-2">Twitter</a> | 
                        <a href="#facebook" className="ms-2">Facebook</a> | 
                        <a href="#instagram" className="ms-2">Instagram</a>
                    </div>
                </Container>
            </footer>
        </>
    );
}

function AppWrapper() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<App />} />
                <Route path="/StandardResultsPage" element={<StandardResultsPage />} />
                <Route path="/BooleanResultsPage" element={<BooleanResultsPage />} />
                <Route path="/TfidfResultsPage" element={<TfidfResultsPage />} /> {/* Add this line */}
                <Route path="/how-it-works" element={<HowItWorks />} />
                <Route path="/error" element={<ErrorPage />} />
            </Routes>

        </BrowserRouter>
    );
}

export default AppWrapper;