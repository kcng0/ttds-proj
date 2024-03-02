import React from 'react';
import { Container, Navbar, Nav } from 'react-bootstrap';
import { Link } from 'react-router-dom';

function HowItWorks() {
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

            <Container className="my-5">
                <h2>How It Works</h2>
                <p>This section should explain the process of how users can utilize your FactChecker service. Include information such as:</p>
                <ul>
                    <li>How to perform a search.</li>
                    <li>How results are generated and presented.</li>
                    <li>Any unique features or considerations of your service.</li>
                </ul>
            </Container>
        </>
    );
}

export default HowItWorks;

