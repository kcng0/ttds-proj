import React from "react";
import {
  Container,
} from "react-bootstrap";
import logoImage from "./logo.png";
import SearchBar from "./SearchBar";
function SearchComponent(top_children, bottom_children) {

  return (
    <>
      <Container
        className="d-flex flex-column justify-content-center align-items-center"
        style={{ minHeight: "80vh" }}
      >
        <div className="text-center">
          <img
            src={logoImage}
            alt="FactChecker Logo"
            style={{ maxWidth: "350px", width: "100%", marginBottom: "20px" }}
          />
          <SearchBar />
        </div>
      </Container>
    </>
  );
}

export default SearchComponent;
