// At the top of your BooleanResultsPage.js, make sure to import the fetchSearchBoolean function
import React, { useState } from 'react';
import { fetchSearchBoolean } from './api'; // Make sure this is the correct path to your API functions
import { Container, Navbar, Nav, InputGroup, FormControl, Button, Card, Pagination, Badge } from 'react-bootstrap';
import { BsSearch } from 'react-icons/bs';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

function BooleanResultsPage() {
    const { searchResults } = useLocation().state || { searchResults: [] }; // Default to empty array if no state
    let navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');

    const performSearch = async (searchTerm) => {
        try {
            const results = await fetchSearchBoolean(searchTerm);
            navigate('/BooleanResultsPage', { state: { searchResults: results, searchType: 'boolean' } });
        } catch (error) {
            console.error('Error fetching boolean search results:', error);
            // Optionally set an error message in state and display in UI
        }
    };

    const handleSearch = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent the default form submission behavior
            performSearch(searchQuery); // Perform the search with the current query
        }
    };

    const handleSearchClick = () => {
        performSearch(searchQuery); // Perform the search when the button is clicked
    };

    const getSentimentBadgeVariant = (sentiment) => {
        switch (sentiment) {
            case 'positive':
                return 'success'; // Green
            case 'negative':
                return 'danger'; // Red
            case 'neutral':
                return 'secondary'; // Grey
            default:
                return 'dark'; // Default color
        }
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
                        placeholder="Enter boolean search terms"
                        aria-label="Boolean Search"
                        aria-describedby="basic-addon2"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        onKeyPress={handleSearch}
                    />
                    <Button variant="outline-secondary" id="button-addon2" onClick={handleSearchClick}>
                        <BsSearch />
                    </Button>
                </InputGroup>

                <h2>Boolean Search Results</h2>
                <ul className="list-unstyled">
                    {searchResults.map((result, index) => (
                        <li key={index} className="mb-3">
                            <Card>
                                <Card.Body>
                                    <Card.Title>{result.title}</Card.Title>
                                    <Badge bg={getSentimentBadgeVariant(result.sentiment)} className="me-2">
                                        {result.sentiment.charAt(0).toUpperCase() + result.sentiment.slice(1)}
                                    </Badge>
                                    <Badge bg="dark" className="me-2">
                                            {result.sentiment.charAt(0).toUpperCase() + result.sentiment.slice(1)}
                                        </Badge>
                                    <Card.Text>
                                        <strong>Date:</strong> {result.date}<br />
                                        <strong>Summary:</strong> {result.summary}
                                    </Card.Text>
                                    <Button variant="primary" href={result.url}>Read More</Button>
                                </Card.Body>
                            </Card>
                        </li>
                    ))}
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

export default BooleanResultsPage;
