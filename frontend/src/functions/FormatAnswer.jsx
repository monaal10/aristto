import { findReferences} from 'functions/ReferenceFunctions.jsx'
import MarkdownIt from 'markdown-it'
import { Tooltip } from '@mui/material'
import React, { useMemo } from 'react'
import { ReferenceTooltip } from 'components/ReferenceTooltip.jsx'
import FormattedTable from '../components/FormattedTable'

const FormatAnswer = ({ content, refs, handleReferenceClick }) => {
  // Check if content contains a table
  const hasTable = content && content.includes('|') && content.includes('|-');

  // Create reference number map
  const refToNumberMap = useMemo(() => {
    const map = new Map();
    refs.forEach((ref, index) => {
      map.set(ref.reference_id, index + 1);
    });
    return map;
  }, [refs]);

  // If we have a table, handle it specially
  if (hasTable) {
    // Extract table and surrounding content
    const lines = content.split('\n');
    let tableStartIndex = -1;
    let tableEndIndex = -1;

    // Find table boundaries
    for (let i = 0; i < lines.length; i++) {
      if (lines[i].trim().startsWith('|')) {
        if (tableStartIndex === -1) tableStartIndex = i;
        tableEndIndex = i;
      } else if (tableStartIndex !== -1 && tableEndIndex !== -1 && !lines[i].trim().startsWith('|')) {
        // We're past the end of the table
        break;
      }
    }

    if (tableStartIndex !== -1 && tableEndIndex !== -1) {
      // Split content into before table, table, and after table
      const beforeTable = lines.slice(0, tableStartIndex).join('\n');
      const tableContent = lines.slice(tableStartIndex, tableEndIndex + 1).join('\n');
      const afterTable = lines.slice(tableEndIndex + 1).join('\n');

      // Render each part separately
      return (
        <div className="markdown-content">
          {/* Render content before table */}
          {beforeTable && <FormatAnswer content={beforeTable} refs={refs} handleReferenceClick={handleReferenceClick} />}

          {/* Render table with refToNumberMap */}
          <FormattedTable
            tableData={tableContent}
            refs={refs}
            refToNumberMap={refToNumberMap}
            handleReferenceClick={handleReferenceClick}
          />

          {/* Render content after table */}
          {afterTable && <FormatAnswer content={afterTable} refs={refs} handleReferenceClick={handleReferenceClick} />}
        </div>
      );
    }
  }

  const parts = findReferences(content, refs);

  // Process parts into sections (blocks) that respect markdown structure
  const processPartsIntoSections = (parts) => {
    const sections = [];
    let currentSection = null;
    let headerBuffer = '';

    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];

      if (part.type === 'text') {
        // Split the text by possible block delimiters (headers)
        const contentLines = part.content.split('\n');

        for (let j = 0; j < contentLines.length; j++) {
          const line = contentLines[j];

          // Check if this line is a header
          if (/^\s*#{1,6}\s+/.test(line)) {
            // If we have a current section or header buffer, finalize it
            if (currentSection || headerBuffer) {
              if (headerBuffer) {
                sections.push({
                  type: 'header',
                  content: headerBuffer
                });
                headerBuffer = '';
              } else if (currentSection) {
                sections.push(currentSection);
                currentSection = null;
              }
            }

            // Start a new header
            headerBuffer = line;

            // If this is the last line of the part, finalize the header
            if (j === contentLines.length - 1) {
              sections.push({
                type: 'header',
                content: headerBuffer
              });
              headerBuffer = '';
            }
          } else {
            // Regular line

            // If we have a header buffer, append this line to it if it's part of a multi-line header
            if (headerBuffer && j === 0) {
              headerBuffer += '\n' + line;

              // If this is the last line, finalize the header
              if (j === contentLines.length - 1) {
                sections.push({
                  type: 'header',
                  content: headerBuffer
                });
                headerBuffer = '';
              }
            } else {
              // Finalize any header buffer
              if (headerBuffer) {
                sections.push({
                  type: 'header',
                  content: headerBuffer
                });
                headerBuffer = '';
              }

              // Regular line belongs to a paragraph
              if (!currentSection) {
                currentSection = {
                  type: 'paragraph',
                  parts: []
                };
              }

              // If this isn't the first line and we have an active paragraph,
              // add a space or newline to separate from the previous line
              if (j > 0 && currentSection.parts.length > 0 &&
                currentSection.parts[currentSection.parts.length - 1].type === 'text') {
                currentSection.parts[currentSection.parts.length - 1].content +=
                  (line.trim() === '' ? '\n\n' : ' ');
              }

              // Add this line to the current paragraph
              if (line.trim() !== '' || j === 0) {
                currentSection.parts.push({
                  type: 'text',
                  content: line
                });
              }

              // If this is a blank line and not the first line, it's a paragraph break
              if (line.trim() === '' && j > 0) {
                if (currentSection && currentSection.parts.length > 0) {
                  sections.push(currentSection);
                  currentSection = null;
                }
              }
            }
          }
        }
      } else if (part.type === 'reference') {
        // Reference part - add to the current paragraph
        if (!currentSection) {
          currentSection = {
            type: 'paragraph',
            parts: []
          };
        }

        currentSection.parts.push(part);
      }
    }

    // Add the final section if it has content
    if (headerBuffer) {
      sections.push({
        type: 'header',
        content: headerBuffer
      });
    } else if (currentSection && currentSection.parts.length > 0) {
      sections.push(currentSection);
    }

    return sections;
  };

  // Get sections from parts
  const sections = processPartsIntoSections(parts);

  // Render a header section
  const renderHeader = (section, sectionIndex) => {
    const md = new MarkdownIt({
      html: true,    // allow HTML tags in the markdown source
      breaks: false,
      linkify: true,
    });
    const html = md.render(section.content);
    return (
      <div key={`header-${sectionIndex}`} dangerouslySetInnerHTML={{ __html: html }}></div>
    );
  };

  // Render a paragraph section with mixed content (text and references)
  const renderParagraph = (section, sectionIndex) => {
    const md = new MarkdownIt({
      html: true,    // allow HTML tags in the markdown source
      breaks: false,
      linkify: true,
    });

    // Check if the paragraph contains code blocks
    const hasCodeBlock = section.parts.some(part =>
      part.type === 'text' && part.content.includes('```')
    );

    // If the paragraph contains code blocks, render it as a whole
    if (hasCodeBlock) {
      // Reconstruct the full paragraph content
      const fullContent = section.parts.map(part => {
        if (part.type === 'text') {
          return part.content;
        } else if (part.type === 'reference') {
          const refNumber = refToNumberMap.get(part.refId);
          return `[${refNumber}]`;
        }
        return '';
      }).join('');

      // Render the full content with code blocks intact
      const html = md.render(fullContent);
      return (
        <div
          key={`para-${sectionIndex}`}
          dangerouslySetInnerHTML={{ __html: html }}
        />
      );
    }

    // Otherwise, use the original rendering logic for paragraphs without code blocks
    return (
      <p key={`para-${sectionIndex}`}>
        {section.parts.map((part, partIndex) => {
          if (part.type === 'text') {
            const html = md.renderInline(part.content);
            return (
              <span
                key={`text-${sectionIndex}-${partIndex}`}
                className="inline"
                dangerouslySetInnerHTML={{ __html: html }}
              />
            );
          } else if (part.type === 'reference') {
            const reference = refs.find(ref => ref.reference_id === part.refId);
            const refNumber = refToNumberMap.get(part.refId);
            return (
              <Tooltip
                key={`ref-${sectionIndex}-${partIndex}`}
                title={<ReferenceTooltip reference={reference} />}
                placement="top"
                componentsProps={{
                  tooltip: { sx: { backgroundColor: 'transparent', p: 0 } },
                  arrow: { sx: { color: 'transparent' } }
                }}
              >
            <span
              onClick={() => handleReferenceClick(part.refId)}
              className="cursor-pointer text-blue-600 underline hover:text-blue-800"
              style={{ display: 'inline' }}
            >
              [{refNumber}]
            </span>
              </Tooltip>
            );
          }
          return null
        })}
      </p>
    );
  };

  // Render all sections
  return (
    <div className="markdown-content">
      {sections.map((section, sectionIndex) => {
        if (section.type === 'header') {
          return renderHeader(section, sectionIndex);
        } else if (section.type === 'paragraph') {
          return renderParagraph(section, sectionIndex);
        }
        return null;
      })}
    </div>
  );
};

export default FormatAnswer;
