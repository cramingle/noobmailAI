#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

// Get __dirname equivalent in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const BASE_URL = 'https://noobmail.ai';
const OUTPUT_FILE = path.join(__dirname, '../static/sitemap.xml');
const ROUTES_DIR = path.join(__dirname, '../src/routes');

// Get current date in YYYY-MM-DD format
const getCurrentDate = () => {
  const date = new Date();
  return date.toISOString().split('T')[0];
};

// Function to discover routes from the filesystem
const discoverRoutes = (dir, baseRoute = '') => {
  let routes = [];
  
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const itemPath = path.join(dir, item);
    const stat = fs.statSync(itemPath);
    
    if (stat.isDirectory()) {
      // Skip directories that start with underscore or dot
      if (item.startsWith('_') || item.startsWith('.')) continue;
      
      // Handle dynamic routes with [param]
      const routePart = item.startsWith('[') ? '' : item;
      const newBaseRoute = baseRoute + (routePart ? '/' + routePart : '');
      
      // Recursively discover nested routes
      const nestedRoutes = discoverRoutes(itemPath, newBaseRoute);
      routes = [...routes, ...nestedRoutes];
    } else if (item === '+page.svelte') {
      // Found a page, add its route
      routes.push(baseRoute || '/');
    }
  }
  
  return routes;
};

// Generate sitemap XML
const generateSitemap = (routes) => {
  const today = getCurrentDate();
  
  let xml = '<?xml version="1.0" encoding="UTF-8"?>\n';
  xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n';
  
  // Add each route to the sitemap
  routes.forEach(route => {
    const url = `${BASE_URL}${route === '/' ? '' : route}`;
    const priority = route === '/' ? '1.0' : '0.8';
    const changefreq = route === '/' ? 'weekly' : 'monthly';
    
    xml += '  <url>\n';
    xml += `    <loc>${url}</loc>\n`;
    xml += `    <lastmod>${today}</lastmod>\n`;
    xml += `    <changefreq>${changefreq}</changefreq>\n`;
    xml += `    <priority>${priority}</priority>\n`;
    xml += '  </url>\n';
  });
  
  xml += '</urlset>';
  
  return xml;
};

// Main execution
try {
  console.log('Discovering routes...');
  const routes = discoverRoutes(ROUTES_DIR);
  console.log(`Found ${routes.length} routes`);
  
  console.log('Generating sitemap...');
  const sitemap = generateSitemap(routes);
  
  // Ensure the directory exists
  const dir = path.dirname(OUTPUT_FILE);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  
  // Write the sitemap to file
  fs.writeFileSync(OUTPUT_FILE, sitemap);
  console.log(`Sitemap written to ${OUTPUT_FILE}`);
} catch (error) {
  console.error('Error generating sitemap:', error);
  process.exit(1);
} 