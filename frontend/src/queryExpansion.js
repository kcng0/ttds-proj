// QueryExpansion.js
import React, { useEffect, useState } from 'react';
import { fetchQueryExpansions } from './api'; // Adjust the import path as necessary

const QueryExpansion = ({ onQuerySelect, currentQuery }) => { // Ensure currentQuery is received as a prop
  const [expansions, setExpansions] = useState([]);

  useEffect(() => {
    //console.log("useEffect triggered with currentQuery:", currentQuery);
    const getExpansions = async () => {
      if (currentQuery) {
        const data = await fetchQueryExpansions(currentQuery);
        //console.log("Data in QE:", data); // Debugging
  
        // Adjust this line if your data is an array of strings
        setExpansions(data.map(query => ({ query })));
      }
    };
    getExpansions();
  }, [currentQuery]);
  

//test 
// const replacementStrings = [
//     "Trump",
//     "US President",
//     "Politics"
//   ];
//   useEffect(() => {
//     const getExpansions = async () => {
//       await fetchQueryExpansions(); // Fetch expansions, but we'll not use the response directly
//       // Set expansions to the predefined replacement strings
//       setExpansions(replacementStrings.map(query => ({ query })));
//     };
//     getExpansions();
//   }, []);

const expansionStyle = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  marginTop: '20px',
};

const expansionItemStyle = {
  backgroundColor: '#f0f0f0',
  color: '#333',
  border: '1px solid #ddd',
  borderRadius: '5px',
  padding: '10px',
  margin: '5px 0',
  cursor: 'pointer',
  width: '80%',
  textAlign: 'center',
  boxSizing: 'border-box',
  transition: 'background-color 0.3s',
  display: 'inline-block', // Ensure it's treated as clickable
};

// Function to handle click on an expanded query
const handleExpansionClick = (query) => {
  onQuerySelect(query); // Call the parent component's handler with the selected query
};

return (
  <div style={expansionStyle}>
    {expansions.length > 0 && <span>Did you mean:</span>}
    {expansions.map((expansion, index) => (
      <div
        key={index}
        style={expansionItemStyle}
        onClick={() => handleExpansionClick(expansion.query)}
        onMouseOver={(e) => (e.target.style.backgroundColor = '#e0e0e0')}
        onMouseOut={(e) => (e.target.style.backgroundColor = '#f0f0f0')}
        role="button" // Accessibility improvement for screen readers
        tabIndex="0" // Make it focusable
      >
        {expansion.query}
      </div>
    ))}
  </div>
);
};


export default QueryExpansion;
