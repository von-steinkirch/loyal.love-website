#!/usr/bin/env node

import fs from 'fs';
import path from 'path';


function fixLinks(htmlContent, filePath) {

    let fixedContent = htmlContent.replace(
        /href="(?!https?:\/\/)([^"]+)"/g,
        (match, href) => {
            if (href.startsWith('data:') || href.startsWith('#')) {
                return match;
            }
            const absolutePath = path.resolve(path.dirname(filePath), href);
            const relativePath = path.relative(process.cwd(), absolutePath);
            return `href="${relativePath}"`;
        }
    );

    fixedContent = fixedContent.replace(
        /src="(?!https?:\/\/)([^"]+)"/g,
        (match, src) => {
            if (src.startsWith('data:')) {
                return match;
            }
            const absolutePath = path.resolve(path.dirname(filePath), src);
            const relativePath = path.relative(process.cwd(), absolutePath);
            return `src="${relativePath}"`;
        }
    );

    return fixedContent;
}

function processFiles() {
    const htmlFiles = [
        'index.html',
        ...fs.readdirSync('chapters').filter(file => file.endsWith('.html')),
        ...fs.readdirSync('shared').filter(file => file.endsWith('.html'))
    ];

    htmlFiles.forEach(file => {
        const filePath = path.join(process.cwd(), file);
        if (fs.existsSync(filePath)) {
            const content = fs.readFileSync(filePath, 'utf8');
            const fixedContent = fixLinks(content, filePath);
            fs.writeFileSync(filePath, fixedContent);
        }
    });
}

processFiles();
