import React, { useState } from 'react';
import { fetchSearchBoolean } from './api';
import { Container, Navbar, Nav, InputGroup, FormControl, Button, Card, Pagination, Badge } from 'react-bootstrap';
import { BsSearch } from 'react-icons/bs';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';

function BooleanResultsPage() {
    const { searchResults } = useLocation().state || { searchResults: [] };
    let navigate = useNavigate();
    const [searchQuery, setSearchQuery] = useState('');
    const [elapsedTime, setElapsedTime] = useState(null);
    const [currentPage, setCurrentPage] = useState(1);
    const resultsPerPage = 5;

    const performSearch = async (searchTerm) => {
        try {
            const startTime = performance.now();
            const results = await fetchSearchBoolean(searchTerm);
            const endTime = performance.now();
            const elapsed = endTime - startTime;
            setElapsedTime(elapsed);

            navigate('/BooleanResultsPage', { state: { searchResults: results, searchType: 'boolean' } });
        } catch (error) {
            console.error('Error fetching boolean search results:', error);
            // Optionally set an error message in state and display in UI
        }
    };

    const handleSearch = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            setCurrentPage(1); // Reset to the first page when performing a new search
            performSearch(searchQuery);
        }
    };

    const handleSearchClick = () => {
        setCurrentPage(1); // Reset to the first page when performing a new search
        performSearch(searchQuery);
    };

    const getSentimentBadgeVariant = (sentiment) => {
        switch (sentiment) {
            case 'positive':
                return 'success';
            case 'negative':
                return 'danger';
            case 'neutral':
                return 'secondary';
            default:
                return 'dark';
        }
    };

    const indexOfLastResult = currentPage * resultsPerPage;
    const indexOfFirstResult = indexOfLastResult - resultsPerPage;
    const currentResults = searchResults.slice(indexOfFirstResult, indexOfLastResult);

    const paginate = (pageNumber) => setCurrentPage(pageNumber);

    const renderPaginationItems = () => {
        const pageNumbers = Math.ceil(searchResults.length / resultsPerPage);
        const items = [];
        for (let number = 1; number <= pageNumbers; number++) {
            items.push(
                <Pagination.Item key={number} active={number === currentPage} onClick={() => paginate(number)}>
                    {number}
                </Pagination.Item>
            );
        }
        return items;
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
                {//elapsedTime !== null && <p>Search took {elapsedTime.toFixed(2)} milliseconds.</p>
                }
                

                <ul className="list-unstyled">
                    {currentResults.map((result, index) => (
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
                    <Pagination>{renderPaginationItems()}</Pagination>
                </Container>
            </Container>
        </>
    );
}

export default BooleanResultsPage;
