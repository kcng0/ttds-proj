import React, { useState } from 'react';
import { Container, Navbar, Nav, InputGroup, FormControl, Button, Card, Pagination } from 'react-bootstrap';
import { BsSearch } from 'react-icons/bs';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import { fetchSearchResults } from './api';

function StandardResultsPage() {
    const { searchResults, searchType } = useLocation().state || { searchResults: [], searchType: 'standard' };
    let navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');

    // Function to handle the search input change
    const handleSearchInputChange = (e) => {
        setSearchQuery(e.target.value);
    };

    // Function to perform the search
    const performSearch = async (searchTerm, page = 1) => {
        try {
            const results = await fetchSearchResults(searchTerm, null, page); // Assuming year is not used here
            navigate('/StandardResultsPage', { state: { searchResults: results, searchType: 'standard' } });
        } catch (error) {
            console.error('Error fetching standard search results:', error);
        }
    };

    // Function to handle the Enter key press or button click for search
    const handleSearch = (e) => {
        if (e.key === 'Enter' || e.type === 'click') {
            e.preventDefault(); // Prevent the default form submission behavior
            performSearch(searchQuery);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent the default form submission behavior
            performSearch(searchQuery);
        }
    };
    
    // Function to handle the button click for search
    const handleClick = () => {
        performSearch(searchQuery);
    };


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

            <Container>
            <InputGroup className="mb-4 mt-3">
    <FormControl
        placeholder="Enter search terms"
        aria-label="Search"
        value={searchQuery}
        onChange={handleSearchInputChange}
        onKeyPress={handleKeyPress} // Only handles the Enter key press
    />
    <Button variant="outline-secondary" id="button-addon2" onClick={handleClick}>
        <BsSearch />
    </Button>
</InputGroup>

                <h2>{`${searchType.charAt(0).toUpperCase() + searchType.slice(1)} Search Results`}</h2>
                <ul>
                    {searchType === 'standard' && Array.isArray(searchResults.results) ? (
                        searchResults.results.map((result, index) => (
                            <li key={index}>{result}</li>
                        ))
                    ) : searchType === 'boolean' && Array.isArray(searchResults) ? (
                        searchResults.map((result, index) => (
                            <li key={index}>
                                <Card>
                                    <Card.Body>
                                        <Card.Title>{result.title}</Card.Title>
                                        <Card.Text>{result.summary}</Card.Text>
                                        <Button variant="primary" href={result.url}>Read More</Button>
                                    </Card.Body>
                                </Card>
                            </li>
                        ))
                    ) : <li>No results found</li>}
                </ul>

                <Container className="d-flex justify-content-center mt-4">
                    <Pagination>
                        <Pagination.Item>{1}</Pagination.Item>
                        <Pagination.Item>{2}</Pagination.Item>
                        {/* Add more items as needed */}
                    </Pagination>
                </Container>
            </Container>
        </>
    );
}

export default StandardResultsPage;