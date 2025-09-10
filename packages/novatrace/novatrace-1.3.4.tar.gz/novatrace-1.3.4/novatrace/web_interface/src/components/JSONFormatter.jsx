import React from 'react'

// Helper function to clean escaped strings
const cleanEscapedString = (str) => {
  return str
    .replace(/\\'/g, "'")
    .replace(/\\n/g, '\n')
    .replace(/\\t/g, '\t')
    .replace(/\\r/g, '\r')
    .replace(/\\"/g, '"')
    .replace(/\\\\/g, '\\')
}

// Nueva función para limpiar JSONs escapados dentro de texto
const cleanEscapedJSON = (str) => {
  // Detectar si el texto contiene JSON escapado (varios patrones)
  if (str.includes('\\{') || str.includes('\\"') || str.includes('\\u') || 
      str.includes('\\\n') || str.includes('{\\\n') || str.includes('\\\\"')) {
    
    console.log(`🔍 cleanEscapedJSON - Input detected as escaped:`, str.substring(0, 50) + '...')
    
    try {
      // Primero, intentar parsear como JSON para decodificar las secuencias de escape
      const unescaped = JSON.parse(`"${str}"`)
      console.log(`🔍 cleanEscapedJSON - After JSON.parse:`, unescaped.substring(0, 50) + '...')
      
      // Luego verificar si el contenido es JSON válido
      if ((unescaped.startsWith('{') && unescaped.endsWith('}')) || 
          (unescaped.startsWith('[') && unescaped.endsWith(']'))) {
        try {
          const parsed = JSON.parse(unescaped)
          const formatted = JSON.stringify(parsed, null, 2)
          console.log(`✅ cleanEscapedJSON - Formatted JSON:`, formatted.substring(0, 50) + '...')
          return formatted
        } catch (e) {
          console.log(`⚠️ cleanEscapedJSON - Not valid JSON, returning unescaped:`, e.message)
          // Si no es JSON válido, devolver el texto decodificado
          return unescaped
        }
      }
      console.log(`🔍 cleanEscapedJSON - Not JSON structure, returning unescaped`)
      return unescaped
    } catch (e) {
      console.log(`❌ cleanEscapedJSON - JSON.parse failed, trying manual cleaning:`, e.message)
      // Si falla el parsing, intentar limpiar manualmente
      let cleaned = str
        // Primero limpiar el patrón específico {\\ -> {
        .replace(/\{\\/g, '{')       // {\\ -> {
        // Luego limpiar TODOS los escapes de final de línea
        .replace(/,\\\\/g, ',')      // ,\\ -> ,
        .replace(/\\\\\n/g, '\n')    // \\n -> \n  
        .replace(/\\\n/g, '\n')      // \n -> newline
        // Otros escapes dobles específicos
        .replace(/\\\\\t/g, '\t')    // \\t -> \t
        .replace(/\\\\\"/g, '"')     // \\" -> "
        .replace(/\\\\\'/g, "'")     // \\' -> '
        // Luego limpiar escapes simples restantes
        .replace(/\\\\/g, '\\')
        .replace(/\\"/g, '"')
        .replace(/\\n/g, '\n')
        .replace(/\\t/g, '\t')
        .replace(/\\u([0-9a-fA-F]{4})/g, (match, code) => {
          return String.fromCharCode(parseInt(code, 16))
        })
      
      console.log(`🔧 cleanEscapedJSON - Manual cleaning result:`, cleaned.substring(0, 50) + '...')
      
      // Intentar parsear el resultado limpio como JSON
      if ((cleaned.startsWith('{') && cleaned.endsWith('}')) || 
          (cleaned.startsWith('[') && cleaned.endsWith(']'))) {
        try {
          const parsed = JSON.parse(cleaned)
          const formatted = JSON.stringify(parsed, null, 2)
          console.log(`✅ cleanEscapedJSON - Successfully formatted cleaned JSON`)
          return formatted
        } catch (e2) {
          console.log(`⚠️ cleanEscapedJSON - Cleaned text is not valid JSON, returning as-is:`, e2.message)
          return cleaned
        }
      }
      
      return cleaned
    }
  }
  console.log(`➡️ cleanEscapedJSON - No escapes detected, returning original`)
  return str
}

// Helper to convert Python-style to JSON
const pythonToJSON = (str) => {
  return str
    .replace(/'/g, '"')
    .replace(/\bTrue\b/g, 'true')
    .replace(/\bFalse\b/g, 'false')
    .replace(/\bNone\b/g, 'null')
}

// Universal parser for any complex structure with parentheses
export const parseComplexStructure = (str, structureType) => {
  // Find the content inside the main parentheses
  const match = str.match(new RegExp(`^${structureType}\\(([\\s\\S]*)\\)$`))
  if (!match) return null
  
  const content = match[1]
  const result = { type: structureType }
  
  // Parse key-value pairs with proper nesting handling
  const pairs = extractKeyValuePairs(content)
  
  for (const pair of pairs) {
    const { key, value } = pair
    
    if (key === 'content' && value.startsWith('[') && value.endsWith(']')) {
      // Parse array content (like content=[...])
      result[key] = parseArrayContent(value)
    } else if (value.startsWith('{') && value.endsWith('}')) {
      // Parse object content
      try {
        // Special handling for SQL queries in input objects
        if (value.includes("'query':")) {
          const queryMatch = value.match(/'query':\s*"((?:[^"\\]|\\.)*)"/s)
          if (queryMatch) {
            let query = queryMatch[1]
              .replace(/\\n/g, '\n')
              .replace(/\\"/g, '"')
              .replace(/\\'/g, "'")
              .replace(/\\\\/g, '\\')
              .replace(/\\t/g, '\t')
            
            // Aplicar limpieza adicional de secuencias Unicode
            console.log(`🧹 Cleaning SQL query with Unicode sequences:`, query.substring(0, 100) + '...')
            query = query.replace(/\\u([0-9a-fA-F]{4})/g, (match, code) => {
              return String.fromCharCode(parseInt(code, 16))
            })
            
            // Limpiar escapes adicionales que pueden quedar (como \\\n)
            query = query.replace(/\\\n/g, '\n').replace(/\\\t/g, '\t')
            
            console.log(`✨ SQL query after Unicode cleaning:`, query.substring(0, 100) + '...')
            
            result[key] = { query: query }
            continue
          }
        }
        
        const jsonStr = pythonToJSON(value)
        result[key] = JSON.parse(jsonStr)
      } catch (e) {
        result[key] = { raw: value }
      }
    } else if (value.match(/^[A-Z][a-zA-Z0-9_]*\(/)) {
      // Parse nested structure
      const nestedType = value.match(/^([A-Z][a-zA-Z0-9_]*)\(/)[1]
      result[key] = parseComplexStructure(value, nestedType)
    } else if (value.startsWith("'") && value.endsWith("'")) {
      // String value
      const cleanValue = cleanEscapedString(value.slice(1, -1))
      // Si es un campo de texto que puede contener JSON escapado, limpiarlo
      if (key === 'text' || key === 'content' || key === 'message') {
        console.log(`🧹 Cleaning escaped JSON for key "${key}":`, cleanValue.substring(0, 100) + '...')
        const cleaned = cleanEscapedJSON(cleanValue)
        console.log(`✨ Result after cleaning:`, cleaned.substring(0, 100) + '...')
        result[key] = cleaned
      } else {
        result[key] = cleanValue
      }
    } else if (value === 'None') {
      result[key] = null
    } else if (value === 'True') {
      result[key] = true
    } else if (value === 'False') {
      result[key] = false
    } else if (!isNaN(value) && value !== '') {
      result[key] = Number(value)
    } else {
      result[key] = value
    }
  }
  
  return result
}

// Extract key-value pairs with proper nesting handling
const extractKeyValuePairs = (content) => {
  const pairs = []
  let currentPair = ''
  let depth = 0
  let inQuotes = false
  let quoteChar = null
  let i = 0
  
  while (i < content.length) {
    const char = content[i]
    const prevChar = i > 0 ? content[i - 1] : null
    
    // Handle quotes
    if ((char === '"' || char === "'") && prevChar !== '\\') {
      if (!inQuotes) {
        inQuotes = true
        quoteChar = char
      } else if (char === quoteChar) {
        inQuotes = false
        quoteChar = null
      }
    }
    
    // Handle nesting only when not in quotes
    if (!inQuotes) {
      if (char === '(' || char === '{' || char === '[') {
        depth++
      } else if (char === ')' || char === '}' || char === ']') {
        depth--
      }
    }
    
    // Split on comma at depth 0 and not in quotes
    if (char === ',' && depth === 0 && !inQuotes) {
      const trimmed = currentPair.trim()
      if (trimmed) {
        const parsed = parseKeyValuePair(trimmed)
        if (parsed) pairs.push(parsed)
      }
      currentPair = ''
    } else {
      currentPair += char
    }
    
    i++
  }
  
  // Handle the last pair
  const trimmed = currentPair.trim()
  if (trimmed) {
    const parsed = parseKeyValuePair(trimmed)
    if (parsed) pairs.push(parsed)
  }
  
  return pairs
}

// Parse a single key-value pair
const parseKeyValuePair = (pairStr) => {
  const eqIndex = pairStr.indexOf('=')
  if (eqIndex === -1) return null
  
  const key = pairStr.substring(0, eqIndex).trim()
  const value = pairStr.substring(eqIndex + 1).trim()
  
  return { key, value }
}

// Parse array content like [TextBlock(...), ToolUseBlock(...)]
const parseArrayContent = (arrayStr) => {
  const content = arrayStr.slice(1, -1).trim() // Remove [ ]
  if (!content) return []
  
  const items = []
  let currentItem = ''
  let depth = 0
  let inQuotes = false
  let quoteChar = null
  let i = 0
  
  while (i < content.length) {
    const char = content[i]
    const prevChar = i > 0 ? content[i - 1] : null
    
    if ((char === '"' || char === "'") && prevChar !== '\\') {
      if (!inQuotes) {
        inQuotes = true
        quoteChar = char
      } else if (char === quoteChar) {
        inQuotes = false
        quoteChar = null
      }
    }
    
    if (!inQuotes) {
      if (char === '(' || char === '{' || char === '[') {
        depth++
      } else if (char === ')' || char === '}' || char === ']') {
        depth--
      }
    }
    
    if (char === ',' && depth === 0 && !inQuotes) {
      const trimmed = currentItem.trim()
      if (trimmed) {
        const parsed = parseArrayItem(trimmed)
        if (parsed) items.push(parsed)
      }
      currentItem = ''
    } else {
      currentItem += char
    }
    
    i++
  }
  
  // Handle the last item
  const trimmed = currentItem.trim()
  if (trimmed) {
    const parsed = parseArrayItem(trimmed)
    if (parsed) items.push(parsed)
  }
  
  return items
}

// Parse individual array item (could be TextBlock, ToolUseBlock, etc.)
const parseArrayItem = (itemStr) => {
  const match = itemStr.match(/^([A-Z][a-zA-Z0-9_]*)\(/)
  if (match) {
    const itemType = match[1]
    return parseComplexStructure(itemStr, itemType)
  }
  
  // If it's not a structured object, try to parse as simple value
  if (itemStr.startsWith("'") && itemStr.endsWith("'")) {
    return cleanEscapedString(itemStr.slice(1, -1))
  } else if (itemStr.startsWith('{') && itemStr.endsWith('}')) {
    try {
      const jsonStr = pythonToJSON(itemStr)
      return JSON.parse(jsonStr)
    } catch (e) {
      return { raw: itemStr }
    }
  }
  
  return itemStr
}

// New robust and dynamic parser for any structured data
export const extractJSONContent = (data) => {
  console.log('🔍 extractJSONContent called with:', typeof data, data?.substring(0, 50) + '...')
  
  if (!data) {
    console.log('❌ No data provided')
    return null
  }
  
  let dataStr = data.toString().trim()
  console.log('📝 Data converted to string, length:', dataStr.length)
  
  // Check if data is wrapped in quotes (as stored in database)
  if ((dataStr.startsWith('"') && dataStr.endsWith('"')) || 
      (dataStr.startsWith("'") && dataStr.endsWith("'"))) {
    console.log('🎯 DETECTED: Data is wrapped in quotes - removing outer quotes')
    console.log('🔍 Before quote removal:', dataStr.substring(0, 100) + '...')
    const quoteChar = dataStr[0]
    dataStr = dataStr.slice(1, -1)
    // Unescape any escaped quotes inside
    if (quoteChar === '"') {
      dataStr = dataStr.replace(/\\"/g, '"')
    } else {
      dataStr = dataStr.replace(/\\'/g, "'")
    }
    console.log('✂️ After quote removal:', dataStr.substring(0, 100) + '...')
    console.log('📏 New length:', dataStr.length)
  }

  // Strategy 1: Try direct JSON parsing
  console.log('🧪 Strategy 1: Direct JSON parsing')
  try {
    const parsed = JSON.parse(dataStr)
    console.log('✅ Strategy 1 SUCCESS: Direct JSON parse worked')
    console.log('🔍 Parsed result type:', typeof parsed)
    console.log('🔍 Parsed result preview:', parsed?.substring ? parsed.substring(0, 100) + '...' : parsed)
    return JSON.stringify(parsed, null, 2)
  } catch (e) {
    console.log('❌ Strategy 1 FAILED:', e.message)
    // Continue to other strategies
  }

  // Strategy 2: Parse Message structure with robust parentheses matching
  console.log('🧪 Strategy 2: Message structure parsing')
  if (dataStr.startsWith('Message(')) {
    console.log('✅ Detected Message structure')
    try {
      const result = parseComplexStructure(dataStr, 'Message')
      console.log('🔄 parseComplexStructure result:', result ? 'SUCCESS' : 'FAILED')
      if (result) {
        const jsonResult = JSON.stringify(result, null, 2)
        console.log('✅ Strategy 2 SUCCESS: Message parsed')
        return jsonResult
      }
    } catch (e) {
      console.warn('❌ Strategy 2 ERROR:', e)
    }
  } else {
    console.log('⏭️ Not a Message structure, skipping')
  }

  // Strategy 3: Parse any other structured object
  console.log('🧪 Strategy 3: Other structured object parsing')
  const structureMatch = dataStr.match(/^([A-Z][a-zA-Z0-9_]*)\(/)
  if (structureMatch) {
    console.log('✅ Detected structure:', structureMatch[1])
    try {
      const structureType = structureMatch[1]
      const result = parseComplexStructure(dataStr, structureType)
      console.log('🔄 parseComplexStructure result for', structureType, ':', result ? 'SUCCESS' : 'FAILED')
      if (result) {
        const jsonResult = JSON.stringify(result, null, 2)
        console.log('✅ Strategy 3 SUCCESS: Structure parsed')
        return jsonResult
      }
    } catch (e) {
      console.warn('❌ Strategy 3 ERROR:', e)
    }
  } else {
    console.log('⏭️ No structured object detected, skipping')
  }

  // Strategy 4: Extract any JSON-like object
  console.log('🧪 Strategy 4: JSON-like object extraction')
  const jsonMatch = dataStr.match(/\{[\s\S]*\}/)
  if (jsonMatch) {
    console.log('✅ Found JSON-like content')
    try {
      const jsonStr = pythonToJSON(jsonMatch[0])
      const parsed = JSON.parse(jsonStr)
      const result = JSON.stringify(parsed, null, 2)
      console.log('✅ Strategy 4 SUCCESS: JSON extracted')
      return result
    } catch (e) {
      console.log('❌ Strategy 4 FAILED:', e.message)
    }
  } else {
    console.log('⏭️ No JSON-like content found, skipping')
  }

  console.log('💥 ALL STRATEGIES FAILED - returning null')
  return null
}

// Helper: convert Python dict to JSON
const pythonDictToJSON = (str) => {
  return str
    .replace(/'/g, '"')
    .replace(/\bNone\b/g, 'null')
    .replace(/\bTrue\b/g, 'true')
    .replace(/\bFalse\b/g, 'false')
}

// Dynamic formatter for any type of structured data
export const formatAnyStructure = (dataStr) => {
  // Strategy 1: Handle Message structures dynamically
  if (dataStr.includes('Message(') && dataStr.includes('content=[')) {
    const messageMatch = dataStr.match(/Message\(([^)]*(?:\([^)]*\)[^)]*)*)\)/s)
    if (messageMatch) {
      const messageContent = messageMatch[1]
      let formattedContent = 'Message:\n'
      
      // Extract all key-value pairs from message level
      const messageKvPattern = /([a-zA-Z_][a-zA-Z0-9_]*)='([^']*(?:\\.[^']*)*)'|([a-zA-Z_][a-zA-Z0-9_]*)=([^,)]+)/g
      let messageKvMatch
      while ((messageKvMatch = messageKvPattern.exec(messageContent)) !== null) {
        const key = messageKvMatch[1] || messageKvMatch[3]
        const value = messageKvMatch[2] || messageKvMatch[4]
        
        if (key !== 'content' && key !== 'usage') {
          formattedContent += `  ${key}: ${value}\n`
        }
      }
      
      // Extract content array
      const contentMatch = messageContent.match(/content=\[(.*?)\](?=,\s*[a-zA-Z_]+=|\))/s)
      if (contentMatch) {
        const contentStr = contentMatch[1]
        formattedContent += '\nContent:\n'
        
        // Dynamic block detection - find any type of structure
        const anyBlockPattern = /([A-Z][a-zA-Z]*(?:Block|Use|Response|Tool|Request|Action)?)\(([^)]*(?:\([^)]*\)[^)]*)*)\)/gs
        let blockMatch
        let blockIndex = 1
        
        while ((blockMatch = anyBlockPattern.exec(contentStr)) !== null) {
          const blockType = blockMatch[1]
          const blockContent = blockMatch[2]
          
          formattedContent += `\n[${blockIndex}. ${blockType}]\n`
          
          // Extract all properties from the block
          const blockKvPattern = /([a-zA-Z_][a-zA-Z0-9_]*)='([^']*(?:\\.[^']*)*)'|([a-zA-Z_][a-zA-Z0-9_]*)=(\{[^}]*(?:\{[^}]*\}[^}]*)*\})|([a-zA-Z_][a-zA-Z0-9_]*)=([^,)]+)/g
          let blockKvMatch
          
          while ((blockKvMatch = blockKvPattern.exec(blockContent)) !== null) {
            const key = blockKvMatch[1] || blockKvMatch[3] || blockKvMatch[5]
            let value = blockKvMatch[2] || blockKvMatch[4] || blockKvMatch[6]
            
            // Clean up escaped characters for text content
            if (key === 'text' || key === 'response') {
              value = value
                .replace(/\\'/g, "'")
                .replace(/\\n/g, '\n')
                .replace(/\\t/g, '\t')
                .replace(/\\"/g, '"')
                .replace(/\\\\/g, '\\')
            }
            
            // Format complex structures like input/output
            if (key === 'input' || key === 'output') {
              if (value.includes("'query':")) {
                const queryMatch = value.match(/['"]query['"]:\s*["']([^"']*(?:\\.[^"']*)*?)["']/)
                if (queryMatch) {
                  const query = queryMatch[1]
                    .replace(/\\n/g, '\n')
                    .replace(/\\"/g, '"')
                    .replace(/\\'/g, "'")
                    .replace(/\\\\/g, '\\')
                    .replace(/\\t/g, '\t')
                  formattedContent += `  ${key}:\n    SQL Query:\n${query.split('\n').map(line => '      ' + line).join('\n')}\n`
                  continue
                }
              }
              
              // Try to format as JSON
              try {
                let jsonStr = value
                  .replace(/'/g, '"')
                  .replace(/True/g, 'true')
                  .replace(/False/g, 'false')
                  .replace(/None/g, 'null')
                
                const parsed = JSON.parse(jsonStr)
                formattedContent += `  ${key}:\n${JSON.stringify(parsed, null, 4).split('\n').map(line => '    ' + line).join('\n')}\n`
                continue
              } catch (e) {
                // Fall through to simple formatting
              }
            }
            
            // Simple key-value formatting
            if (value && value.length > 50) {
              formattedContent += `  ${key}:\n    ${value}\n`
            } else {
              formattedContent += `  ${key}: ${value}\n`
            }
          }
          blockIndex++
        }
      }
      
      // Extract usage if present
      const usageMatch = messageContent.match(/usage=Usage\(([^)]*)\)/)
      if (usageMatch) {
        formattedContent += '\nUsage:\n'
        const usageContent = usageMatch[1]
        const usageKvPattern = /([a-zA-Z_][a-zA-Z0-9_]*)=(\d+)/g
        let usageKvMatch
        while ((usageKvMatch = usageKvPattern.exec(usageContent)) !== null) {
          formattedContent += `  ${usageKvMatch[1]}: ${usageKvMatch[2]}\n`
        }
      }
      
      return formattedContent
    }
  }
  
  // Strategy 2: Handle individual blocks/structures
  const singleBlockPattern = /([A-Z][a-zA-Z]*(?:Block|Use|Response|Tool|Request|Action)?)\(([^)]*(?:\([^)]*\)[^)]*)*)\)/s
  const singleBlockMatch = dataStr.match(singleBlockPattern)
  if (singleBlockMatch) {
    const blockType = singleBlockMatch[1]
    const blockContent = singleBlockMatch[2]
    
    let formattedContent = `${blockType}:\n`
    
    // Extract all properties
    const kvPattern = /([a-zA-Z_][a-zA-Z0-9_]*)='([^']*(?:\\.[^']*)*)'|([a-zA-Z_][a-zA-Z0-9_]*)=(\{[^}]*(?:\{[^}]*\}[^}]*)*\})|([a-zA-Z_][a-zA-Z0-9_]*)=([^,)]+)/g
    let kvMatch
    
    while ((kvMatch = kvPattern.exec(blockContent)) !== null) {
      const key = kvMatch[1] || kvMatch[3] || kvMatch[5]
      let value = kvMatch[2] || kvMatch[4] || kvMatch[6]
      
      // Special formatting for different types of content
      if (key === 'text' || key === 'response') {
        value = value
          .replace(/\\'/g, "'")
          .replace(/\\n/g, '\n')
          .replace(/\\t/g, '\t')
          .replace(/\\"/g, '"')
          .replace(/\\\\/g, '\\')
      }
      
      if (key === 'input' || key === 'output') {
        if (value.includes("'query':")) {
          const queryMatch = value.match(/['"]query['"]:\s*["']([^"']*(?:\\.[^"']*)*?)["']/)
          if (queryMatch) {
            const query = queryMatch[1]
              .replace(/\\n/g, '\n')
              .replace(/\\"/g, '"')
              .replace(/\\'/g, "'")
              .replace(/\\\\/g, '\\')
              .replace(/\\t/g, '\t')
            formattedContent += `  ${key}:\n    SQL Query:\n${query.split('\n').map(line => '      ' + line).join('\n')}\n`
            continue
          }
        }
        
        try {
          let jsonStr = value
            .replace(/'/g, '"')
            .replace(/True/g, 'true')
            .replace(/False/g, 'false')
            .replace(/None/g, 'null')
          
          const parsed = JSON.parse(jsonStr)
          formattedContent += `  ${key}:\n${JSON.stringify(parsed, null, 4).split('\n').map(line => '    ' + line).join('\n')}\n`
          continue
        } catch (e) {
          // Fall through
        }
      }
      
      formattedContent += `  ${key}: ${value}\n`
    }
    
    return formattedContent
  }
  
  return null
}

// Main formatting function - enhanced with dynamic handling
export const formatJSONData = (data) => {
  if (!data) return 'No data'

  try {
    // Case 0: if already an object
    if (typeof data === 'object') {
      return JSON.stringify(data, null, 2)
    }

    let dataStr = data.toString()

    // Case 1: try direct JSON
    try {
      const parsed = JSON.parse(dataStr)
      return JSON.stringify(parsed, null, 2)
    } catch (e) {
      // continue
    }

    // Case 2: Try dynamic structure formatting
    const dynamicFormatted = formatAnyStructure(dataStr)
    if (dynamicFormatted) {
      return dynamicFormatted
    }

    // Case 3: text='...' field with better escape handling
    const textMatch = dataStr.match(/text='([^']*(?:\\.[^']*)*?)'/s)
    if (textMatch) {
      const cleanedText = textMatch[1]
        .replace(/\\'/g, "'")
        .replace(/\\n/g, '\n')
        .replace(/\\t/g, '\t')
        .replace(/\\"/g, '"')
        .replace(/\\\\/g, '\\')
      return cleanedText // clean plain text
    }

    // Case 4: simple input={...} field
    const inputMatch = dataStr.match(/input=(\{.*?\})/)
    if (inputMatch) {
      try {
        const fixed = pythonDictToJSON(inputMatch[1])
        const parsed = JSON.parse(fixed)
        return JSON.stringify(parsed, null, 2)
      } catch (e) {
        return inputMatch[1]
      }
    }

    // Case 5: look for any dict {...} and try
    const jsonMatch = dataStr.match(/\{[\s\S]*?\}/)
    if (jsonMatch) {
      try {
        const fixed = pythonDictToJSON(jsonMatch[0])
        const parsed = JSON.parse(fixed)
        return JSON.stringify(parsed, null, 2)
      } catch (e) {
        // no worries, fallback below
      }
    }

    // Case 6: fallback → format nicely any structure
    if (dataStr.includes('(') && dataStr.includes(')')) {
      return dataStr
        .replace(/([A-Z][a-zA-Z]*)\(/g, '$1(\n  ')
        .replace(/, /g, ',\n  ')
        .replace(/\)/g, '\n)')
    }

    // Last fallback: raw string
    return dataStr
  } catch (err) {
    return String(data)
  }
}

// Get formatted content with view options
export const getContentWithOptions = (data, fieldType) => {
  const extractedJSON = extractJSONContent(data)
  const formatted = formatJSONData(data)
  const smartView = formatAnyStructure(typeof data === 'string' ? data : JSON.stringify(data, null, 2))
  
  return {
    hasExtractedJSON: !!extractedJSON,
    extractedJSON: extractedJSON,
    formatted: formatted,
    smartView: smartView,
    original: data
  }
}

const JSONFormatter = ({ data, fieldType }) => {
  const content = getContentWithOptions(data, fieldType)
  
  return (
    <div className="space-y-2">
      {content.hasExtractedJSON && (
        <div className="bg-green-50 border border-green-200 rounded-md p-3">
          <h5 className="text-sm font-medium text-green-800 mb-2">Parsed JSON:</h5>
          <pre className="text-xs text-green-700 whitespace-pre-wrap overflow-x-auto">
            {content.extractedJSON}
          </pre>
        </div>
      )}
      
      <div className="bg-gray-50 rounded-md p-3">
        <h5 className="text-sm font-medium text-gray-800 mb-2">Formatted View:</h5>
        <pre className="text-xs text-gray-700 whitespace-pre-wrap overflow-x-auto">
          {content.formatted}
        </pre>
      </div>
    </div>
  )
}

export default JSONFormatter
