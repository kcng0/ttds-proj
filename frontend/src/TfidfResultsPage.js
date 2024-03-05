import React, { useState } from 'react';
import { fetchSearchTfidf } from './api';
import { Container, Navbar, Nav, InputGroup, FormControl, Button, Card, Badge, Pagination } from 'react-bootstrap';
import { BsSearch } from 'react-icons/bs';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

function TfidfResultsPage() {
    const location = useLocation();
    const navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');
    const [searchType, setSearchType] = useState('tfidf'); 

    const handleSearchInputChange = (e) => {
        setSearchQuery(e.target.value);
    };

    const performSearch = async (searchTerm) => {
        try {
            const results = await fetchSearchTfidf(searchTerm);
            navigate('/TfidfResultsPage', { state: { searchResults: results, searchType } });
        } catch (error) {
            console.error('Error fetching TF-IDF search results:', error);
            // Optionally, handle the error in the UI
        }
    };

    const handleSearch = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault(); // Prevent form submission
            performSearch(searchQuery);
        }
    };

    const handleSearchClick = () => {
        performSearch(searchQuery);
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


    // Rest of the component remains the same
    const { searchResults } = location.state;


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
                        placeholder="Search TF-IDF terms"
                        aria-label="Search"
                        value={searchQuery}
                        onChange={handleSearchInputChange}
                        onKeyPress={handleSearch}
                    />
                    <Button variant="outline-secondary" id="button-addon2" onClick={handleSearchClick}>
                        <BsSearch />
                    </Button>
                </InputGroup>

                <h2>{`${searchType.charAt(0).toUpperCase() + searchType.slice(1)} Search Results`}</h2>
                <ul>
                    {Array.isArray(searchResults) ? (
                        searchResults.map((result, index) => (
                            <li key={index}>
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
                                            <strong>Score:</strong> {result.score}<br />
                                            <strong>Summary:</strong> {result.summary}
                                        </Card.Text>
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

export default TfidfResultsPage;