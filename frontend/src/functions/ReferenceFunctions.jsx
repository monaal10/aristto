export const findReferences = (text, refs) => {
  if (!text || !refs) return [{ type: 'text', content: text || '' }];

  const parts = [];
  let lastIndex = 0;

  // Create a mapping from reference_id to a sequential display number (1-indexed)
  const refIdToDisplayNumber = {};
  refs.forEach((ref, index) => {
    refIdToDisplayNumber[ref.reference_id] = index + 1;
  });

  // Look for references in square brackets
  const refPattern = /\[([^\]]+)\]/g;
  let match;

  while ((match = refPattern.exec(text)) !== null) {
    // Add text before this reference
    if (match.index > lastIndex) {
      parts.push({ type: 'text', content: text.slice(lastIndex, match.index) });
    }

    // Extract the potential reference content (expected to be a reference id)
    const bracketContent = match[1].trim();

    // Check if this is a valid reference ID using the sequential mapping
    if (refIdToDisplayNumber[bracketContent]) {
      parts.push({
        type: 'reference',
        content: refIdToDisplayNumber[bracketContent].toString(), // Display the sequential number
        refId: bracketContent // Keep original ID for lookup
      });
    } else {
      // If no valid reference, add as plain text
      parts.push({ type: 'text', content: match[0] });
    }

    lastIndex = match.index + match[0].length;
  }

  // Add any remaining text after the last match
  if (lastIndex < text.length) {
    parts.push({ type: 'text', content: text.slice(lastIndex) });
  }

  return parts;
};
