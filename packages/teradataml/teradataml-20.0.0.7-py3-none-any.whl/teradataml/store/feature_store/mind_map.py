"""
Copyright (c) 2025 by Teradata Corporation. All rights reserved.
TERADATA CORPORATION CONFIDENTIAL AND TRADE SECRET

Primary Owner: pradeep.garre@teradata.com
Secondary Owner: adithya.avvaru@teradata.com

This file implements the mind map for Teradata Enterprise Feature Store.
"""

_TD_FS_MindMap_Template = """
<style>
    .mindmap-header-container {
        width: 980px;
        margin: 0 auto;
        border: 1px solid #ccc;
        background: #fafbfc;
        border-radius: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 64px;
        margin-top: 20px;
    }
    .mindmap-header-single {
        width: 100%;
        text-align: center;
        font-size: 1.25em;
        font-weight: 600;
        color: #2d3a4b;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }
    /* ...existing code... */
    #container_fs_i {
            width: 980px;
            margin: 0 auto 40px auto;
            position: relative;
            border: 1px solid #ccc;
            background: #fafbfc;
            border-top: none;
            border-radius: 0;
        }
    .mindmap-inner {
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        align-items: stretch;
        width: 100%;
        margin-bottom: 50px;
        gap: 32px;
        padding-top: 30px;
    }
    .column {
        flex: 1;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        margin: 0;
        position: relative;
        background: #fff;
        border: 1.5px solid #e0e6ef;
        border-radius: 14px;
        box-shadow: 0 2px 8px #0001;
        padding: 0 0 18px 0;
        min-width: 140px;
        min-height: 500px;
        transition: box-shadow 0.2s;
    }
    /* Add left margin to first column and right margin to last column for centering */
    .column#data_sources_col_fs_i {
        margin-left: 32px;
    }
    .column#dataset_catalog_col_fs_i {
        margin-right: 32px;
    }
    .column:hover {
        box-shadow: 0 4px 16px #0002;
    }
    .column-title {
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 10px;
        color: #2d3a4b;
        width: 100%;
        text-align: center;
        border-bottom: 1.5px solid #e0e6ef;
        padding: 16px 0 8px 0;
        background: #f7fafd;
        border-top-left-radius: 14px;
        border-top-right-radius: 14px;
        box-sizing: border-box;
    }
    .box {
        width: 120px;
        min-height: 40px;
        background: #e3eaf2;
        border: 2px solid #7da0ca;
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        /* margin: 16px 0; */
        font-size: 15px;
        color: #2d3a4b;
        position: relative;
        z-index: 2;
        box-shadow: 0 2px 6px #0001;
        transition: box-shadow 0.2s, border-color 0.2s, background 0.2s;
        cursor: pointer;
        word-break: break-word;
        white-space: normal;
        overflow-wrap: break-word;
        padding: 4px 8px;
        text-align: center;
        overflow: hidden;
    }
    .box.highlight {
        /* Slightly brighten and bring to front, but keep original color */
        filter: brightness(1.15);
        box-shadow: 0 0 12px 2px #eab676, 0 2px 6px #0001;
        opacity: 1 !important;
        z-index: 10;
    }
    .box.related {
        /* Gold color for related objects, slightly brightened, bring to front */
        background: #eab676 !important;
        border-color: #e28743 !important;
        filter: brightness(1.10);
        box-shadow: 0 0 8px 1px #e28743 !important, 0 2px 6px #eab676;
        opacity: 1 !important;
        z-index: 9;
    }
    .box.dimmed {
        opacity: 0.20 !important;
        filter: grayscale(0.25) brightness(0.80);
    }
    .feature-box {
        background: #f7e6c7;
        border-color: #e0b96a;
    }
    .dataset-box {
        background: #d6f5e3;
        border-color: #6ac7a0;
    }
    .fp-box {
        background: #f2d6e6;
        border-color: #c76aa0;
    }
    .ds-box {
        background: #e3eaf2;
        border-color: #7da0ca;
    }
    #svg_fs_i {
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        pointer-events: none;
        z-index: 1000;
    }
    .svg-curve {
        transition: filter 0.2s, stroke 0.2s, stroke-width 0.2s, opacity 0.2s;
        filter: none;
    }
    .svg-curve.highlight {
        /* Slightly brighten, keep original color, bring to front */
        filter: brightness(1.15) drop-shadow(0 0 6px #8884);
        stroke-width: 5 !important;
        opacity: 1 !important;
    }
    .svg-curve.related {
        filter: brightness(1.10) drop-shadow(0 0 4px #8882);
        stroke-width: 4 !important;
        opacity: 0.95 !important;
    }
    .svg-curve.dimmed {
        opacity: 0.10 !important;
        filter: grayscale(0.25) brightness(0.80);
    }
</style>
<div class="mindmap-header-container">
    <div class="mindmap-header-single" id="mindmap-header-single">
    Repo: &nbsp;<span style="text-decoration: underline; text-decoration-color: #a3c0e0;">__REPO__</span>&nbsp; (Data Domain: &nbsp;<span style="text-decoration: underline; text-decoration-color: #a3c0e0;">__DATA_DOMAIN__</span>&nbsp;)
    </div>
</div>
<div id="container_fs_i">
    <div class="mindmap-inner">
        <svg id="svg_fs_i"></svg>
        <div class="column" id="data_sources_col_fs_i" style="margin-left: 20px;">
            <div class="column-title">Data Sources</div>
        </div>
        <div class="column" id="feature_processes_col_fs_i">
            <div class="column-title">Feature Processes</div>
        </div>
        <div class="column" id="feature_catalog_col_fs_i">
            <div class="column-title">Feature Catalog</div>
        </div>
        <div class="column" id="dataset_catalog_col_fs_i" style="margin-right: 20px;">
            <div class="column-title">Dataset Catalog</div>
        </div>
    </div>
    <div id="mindmap-timestamp_fs_i" style="position: absolute; right: 24px; bottom: 8px; color: #666; font-size: 10.75px; font-family: 'Segoe UI', Arial, sans-serif; z-index: 2000; pointer-events: none; user-select: none; font-style: italic; font-weight: 600; letter-spacing: 0.1px;">
        <span style="font-style: italic; font-weight: 600; font-size: 10.75px;">Mind map for Feature Store is generated at <span id="mindmap-timestamp-value_fs_i">__MINDMAP_TIMESTAMP__</span>.</span>
    </div>
</div>
<script>
/*
===================== MIND MAP DATA STRUCTURE =====================
The following variables are injected from Python and define the mind map:

1. dataSources: Array of objects, each with 'id' and 'label'.
   Example:
   [
       { id: "ds1_fs_xxx", label: "Data Source 1" },
       { id: "ds2_fs_xxx", label: "Data Source 2" }
   ]

2. featureProcesses: Array of objects, each with 'id' and 'label'.
   Example:
   [
       { id: "fp1_fs_xxx", label: "Feature Process 1" },
       { id: "fp2_fs_xxx", label: "Feature Process 2" }
   ]

3. features: Array of objects, each with 'id' and 'label'.
   Example:
   [
       { id: "f1_fs_xxx", label: "Feature 1" },
       { id: "f2_fs_xxx", label: "Feature 2" }
   ]

4. datasets: Array of objects, each with 'id' and 'label'.
   Example:
   [
       { id: "d1_fs_xxx", label: "Dataset 1" },
       { id: "d2_fs_xxx", label: "Dataset 2" }
   ]

5. dataSourceMap: Object mapping dataSource id to array of featureProcess ids.
   Example:
   {
       "ds1_fs_xxx": ["fp1_fs_xxx", "fp2_fs_xxx"],
       "ds2_fs_xxx": ["fp2_fs_xxx"]
   }

6. featureProcessMap: Object mapping featureProcess id to array of feature ids.
   Example:
   {
       "fp1_fs_xxx": ["f1_fs_xxx", "f2_fs_xxx"],
       "fp2_fs_xxx": ["f2_fs_xxx", "f3_fs_xxx"]
   }

7. datasetFeatureMap: Object mapping dataset id to array of feature ids.
   Example:
   {
       "d1_fs_xxx": ["f1_fs_xxx", "f2_fs_xxx"],
       "d2_fs_xxx": ["f2_fs_xxx", "f3_fs_xxx"]
   }

All ids must be unique and consistent across these variables. The '_fs_xxx' suffix is added for uniqueness.
====================================================================
*/
// --- Mind Map Data ---
var dataSources = __DATA_SOURCES__;
var featureProcesses = __FEATURE_PROCESSES__;
var features = __FEATURES__;
var datasets = __DATASETS__;
var dataSourceMap = __DATA_SOURCE_MAP__;
var featureProcessMap = __FEATURE_PROCESS_MAP__;
var datasetFeatureMap = __DATASET_FEATURE_MAP__;

// ...existing JS code (renderFeatureStoreMindMap, etc.)...
function renderFeatureStoreMindMap(dataSources, featureProcesses, features, datasets, dataSourceMap, featureProcessMap, datasetFeatureMap) {
    // --- Helper: Create Box ---
    function createBox(obj, cls) {
        var div = document.createElement('div');
        div.className = 'box ' + cls;
        div.id = obj.id;
        if (obj.invisible) {
            div.style.opacity = '0';
            div.style.pointerEvents = 'none';
            div.innerHTML = '&nbsp;';
        } else {
            // Show only first 14 characters, add ellipsis if longer, show full label on hover
            var span = document.createElement('span');
            var label = obj.label || '';
            if (label.length > 14) {
                span.textContent = label.slice(0, 14) + '...';
            } else {
                span.textContent = label;
            }
            span.style.display = 'inline-block';
            span.style.width = '100%';
            span.style.whiteSpace = 'nowrap';
            span.style.overflow = 'hidden';
            span.style.textOverflow = 'ellipsis';
            span.title = label;
            div.appendChild(span);
        }
        return div;
    }
    // --- Declare all main DOM elements by ID at the top ---
    var container_fs_v = document.getElementById('container_fs_i');
    var svg_fs_v = document.getElementById('svg_fs_i');
    var dsCol = document.getElementById('data_sources_col_fs_i');
    var fpCol = document.getElementById('feature_processes_col_fs_i');
    var fCol = document.getElementById('feature_catalog_col_fs_i');
    var dCol = document.getElementById('dataset_catalog_col_fs_i');

    // Helper: Add EMPTY label if needed
    function addEmptyLabel(col) {
        var emptyDiv = document.createElement('div');
        emptyDiv.textContent = 'EMPTY';
        emptyDiv.style.color = '#aaa';
        emptyDiv.style.fontSize = '18px';
        emptyDiv.style.fontWeight = 'bold';
        emptyDiv.style.position = 'absolute';
        emptyDiv.style.top = '50%';
        emptyDiv.style.left = '50%';
        emptyDiv.style.transform = 'translate(-50%, -50%)';
        emptyDiv.style.pointerEvents = 'none';
        emptyDiv.style.userSelect = 'none';
        emptyDiv.className = 'empty-label';
        col.appendChild(emptyDiv);
    }

    // Remove all children except column-title
    [dsCol, fpCol, fCol, dCol].forEach(function(col) {
        Array.from(col.children).forEach(function(child) {
            if (!child.classList.contains('column-title')) col.removeChild(child);
        });
    });

    // Helper to spread children vertically with equal space
    function spreadChildren(col, items, boxClass) {
        if (items.length === 0) {
            addEmptyLabel(col);
            return;
        }
        var title = col.querySelector('.column-title');
        var titleHeight = title ? title.offsetHeight : 0;
        var n = items.length;
        var boxHeight = 40; // Should match .box height in CSS
        var topMargin = 16; // Margin between title and first child
        var bottomMargin = 24; // Margin between last child and bottom
        var minGap = 30; // Minimum margin between child boxes
        var colHeight = col.offsetHeight;
        var availableHeight = colHeight - titleHeight - topMargin - bottomMargin;
        var gap = n > 1 ? Math.max((availableHeight - n * boxHeight) / (n - 1), minGap) : (availableHeight - boxHeight) / 2;
        var totalChildrenHeight = n * boxHeight + (n - 1) * gap;
        // If gap is forced to minGap, center the group vertically
        var startY = titleHeight + topMargin;
        if (n > 1 && gap === minGap) {
            var extraSpace = availableHeight - (n * boxHeight + (n - 1) * minGap);
            startY += Math.max(extraSpace / 2, 0);
        }
        if (n === 1) {
            startY += (availableHeight - boxHeight) / 2;
        }
        items.forEach(function(item, i) {
            var box = createBox(item, boxClass);
            box.style.position = 'absolute';
            box.style.left = '50%';
            box.style.transform = 'translateX(-50%)';
            box.style.top = (startY + i * (boxHeight + gap)) + 'px';
            col.appendChild(box);
        });
        col.style.position = 'relative';
    }

    spreadChildren(dsCol, dataSources, 'ds-box');
    spreadChildren(fpCol, featureProcesses, 'fp-box');
    spreadChildren(fCol, features, 'feature-box');
    spreadChildren(dCol, datasets, 'dataset-box');

    // --- Dynamically adjust all main columns to equal height ---
    var minHeight = 500;
    var boxHeight = 40;
    var topMargin = 16;
    var bottomMargin = 24;
    var minGap = 30;
    var titleHeight = dsCol.querySelector('.column-title').offsetHeight;
    function getColumnRequiredHeight(numChildren) {
        if (numChildren === 0) return minHeight;
        // Height = title + topMargin + bottomMargin + children + gaps
        return titleHeight + topMargin + bottomMargin + (numChildren * boxHeight) + ((numChildren - 1) * minGap);
    }
    var dsColHeight = getColumnRequiredHeight(dataSources.length);

    var fpColHeight = getColumnRequiredHeight(featureProcesses.length);
    var fColHeight = getColumnRequiredHeight(features.length);
    var dColHeight = getColumnRequiredHeight(datasets.length);
    var maxColHeight = Math.max(dsColHeight, fpColHeight, fColHeight, dColHeight, minHeight);

    // Add extra bottom margin (e.g., 100px) to the container height
    var containerExtraBottom = 100;
    var containerHeight = maxColHeight + containerExtraBottom;

    // Set all columns to the same height, and container to be larger
    container_fs_v.style.height = containerHeight + 'px';
    container_fs_v.style.minHeight = (minHeight + containerExtraBottom) + 'px';
    svg_fs_v.setAttribute('height', containerHeight);
    svg_fs_v.style.height = containerHeight + 'px';
    dsCol.style.minHeight = dsCol.style.height = maxColHeight + 'px';
    fpCol.style.minHeight = fpCol.style.height = maxColHeight + 'px';
    fCol.style.minHeight = fCol.style.height = maxColHeight + 'px';
    dCol.style.minHeight = dCol.style.height = maxColHeight + 'px';

    function getEntryExitOffset(el, direction) {
        const rect = el.getBoundingClientRect();
        const parentRect = container_fs_v.getBoundingClientRect();
        if (direction === 'right') {
            return {
                x: rect.right - parentRect.left,
                y: rect.top - parentRect.top + rect.height/2
            };
        } else if (direction === 'left') {
            return {
                x: rect.left - parentRect.left,
                y: rect.top - parentRect.top + rect.height/2
            };
        } else {
            return {
                x: rect.left - parentRect.left + rect.width/2,
                y: rect.top - parentRect.top + rect.height/2
            };
        }
    }
    // --- Helper: Draw Curve ---
    function drawCurve(svg, fromElem, toElem, color, fromDir, toDir, meta) {
        if (!fromElem || !toElem) return;
        const from = getEntryExitOffset(fromElem, fromDir);
        const to = getEntryExitOffset(toElem, toDir);
        const x1 = from.x;
        const y1 = from.y;
        const x2 = to.x;
        const y2 = to.y;
        const dx = Math.max(Math.abs(x2 - x1) * 0.3, 40);
        const path = `M${x1},${y1} C${x1+dx},${y1} ${x2-dx},${y2} ${x2},${y2}`;
        const curve = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        curve.setAttribute('d', path);
        curve.setAttribute('stroke', color);
        curve.setAttribute('stroke-width', '3');
        curve.setAttribute('fill', 'none');
        curve.setAttribute('opacity', '0.8');
        curve.classList.add('svg-curve');
        if (meta) {
            curve.dataset.from = meta.from;
            curve.dataset.to = meta.to;
            curve.dataset.type = meta.type;
        }
        svg.appendChild(curve);
    }
    // --- Draw All Curves and Store Meta ---
    function drawMindMapLinks() {
        const svg = svg_fs_v;
        while (svg.firstChild) svg.removeChild(svg.firstChild);
        setTimeout(function() {
            // DataSource to FeatureProcess
            Object.keys(dataSourceMap).forEach(function(dsId) {
                dataSourceMap[dsId].forEach(function(fpId) {
                    drawCurve(svg, document.getElementById(dsId), document.getElementById(fpId), '#7da0ca', 'right', 'left', {from: dsId, to: fpId, type: 'ds-fp'});
                });
            });
            // FeatureProcess to Features
            Object.keys(featureProcessMap).forEach(function(fpId) {
                featureProcessMap[fpId].forEach(function(fId) {
                    drawCurve(svg, document.getElementById(fpId), document.getElementById(fId), '#c76aa0', 'right', 'left', {from: fpId, to: fId, type: 'fp-f'});
                });
            });
            // Features to Datasets (note: map is dataset -> features)
            Object.keys(datasetFeatureMap).forEach(function(dId) {
                datasetFeatureMap[dId].forEach(function(fId) {
                    drawCurve(svg, document.getElementById(fId), document.getElementById(dId), '#6ac7a0', 'right', 'left', {from: fId, to: dId, type: 'f-d'});
                });
            });
            attachHoverEvents();
        }, 100);
    }

    // --- Highlight Logic ---
    function clearHighlights() {
        container_fs_v.querySelectorAll('.box').forEach(function(box) {
            box.classList.remove('highlight', 'related', 'dimmed');
        });
        container_fs_v.querySelectorAll('.svg-curve').forEach(function(curve) {
            curve.classList.remove('highlight', 'related', 'dimmed');
        });
    }

    function attachHoverEvents() {
        // Remove previous listeners by cloning
        container_fs_v.querySelectorAll('.box').forEach(function(box) {
            var newBox = box.cloneNode(true);
            box.parentNode.replaceChild(newBox, box);
        });

        function dimUnrelated(relatedBoxIds, relatedCurveSelector) {
            // Dim unrelated boxes
            container_fs_v.querySelectorAll('.box').forEach(function(box) {
                if (!relatedBoxIds.includes(box.id)) {
                    box.classList.add('dimmed');
                }
            });
            // Dim unrelated curves
            container_fs_v.querySelectorAll('.svg-curve').forEach(function(curve) {
                if (!curve.matches(relatedCurveSelector)) {
                    curve.classList.add('dimmed');
                }
            });
        }

        // Data Sources
        dataSources.forEach(function(ds) {
            var el = document.getElementById(ds.id);
            if (!el) return;
            el.addEventListener('mouseenter', function() {
                clearHighlights();
                el.classList.add('highlight');
                var relatedBoxIds = [ds.id];
                (dataSourceMap[ds.id]||[]).forEach(function(fpId) {
                    var fpEl = document.getElementById(fpId);
                    if (fpEl) fpEl.classList.add('related');
                    relatedBoxIds.push(fpId);
                    container_fs_v.querySelectorAll('.svg-curve[data-from="'+ds.id+'"][data-to="'+fpId+'"]').forEach(function(curve) {
                        if (curve.dataset.type === 'ds-fp') curve.classList.add('highlight');
                    });
                });
                dimUnrelated(relatedBoxIds, '.svg-curve.highlight');
            });
            el.addEventListener('mouseleave', clearHighlights);
        });
        // Feature Processes
        featureProcesses.forEach(function(fp) {
            var el = document.getElementById(fp.id);
            if (!el) return;
            el.addEventListener('mouseenter', function() {
                clearHighlights();
                el.classList.add('highlight');
                var relatedBoxIds = [fp.id];
                // Related Data Sources
                Object.keys(dataSourceMap).forEach(function(dsId) {
                    if ((dataSourceMap[dsId]||[]).includes(fp.id)) {
                        var dsEl = document.getElementById(dsId);
                        if (dsEl) dsEl.classList.add('related');
                        relatedBoxIds.push(dsId);
                        container_fs_v.querySelectorAll('.svg-curve[data-from="'+dsId+'"][data-to="'+fp.id+'"]').forEach(function(curve) {
                            if (curve.dataset.type === 'ds-fp') curve.classList.add('highlight');
                        });
                    }
                });
                // Related Features
                (featureProcessMap[fp.id]||[]).forEach(function(fId) {
                    var fEl = document.getElementById(fId);
                    if (fEl) fEl.classList.add('related');
                    relatedBoxIds.push(fId);
                    container_fs_v.querySelectorAll('.svg-curve[data-from="'+fp.id+'"][data-to="'+fId+'"]').forEach(function(curve) {
                        if (curve.dataset.type === 'fp-f') curve.classList.add('highlight');
                    });
                });
                dimUnrelated(relatedBoxIds, '.svg-curve.highlight');
            });
            el.addEventListener('mouseleave', clearHighlights);
        });
        // Features
        features.forEach(function(f) {
            var el = document.getElementById(f.id);
            if (!el) return;
            el.addEventListener('mouseenter', function() {
                clearHighlights();
                el.classList.add('highlight');
                var relatedBoxIds = [f.id];
                // Related Feature Processes
                Object.keys(featureProcessMap).forEach(function(fpId) {
                    if ((featureProcessMap[fpId]||[]).includes(f.id)) {
                        var fpEl = document.getElementById(fpId);
                        if (fpEl) fpEl.classList.add('related');
                        relatedBoxIds.push(fpId);
                        container_fs_v.querySelectorAll('.svg-curve[data-from="'+fpId+'"][data-to="'+f.id+'"]').forEach(function(curve) {
                            if (curve.dataset.type === 'fp-f') curve.classList.add('highlight');
                        });
                    }
                });
                // Related Datasets
                Object.keys(datasetFeatureMap).forEach(function(dId) {
                    if ((datasetFeatureMap[dId]||[]).includes(f.id)) {
                        var dEl = document.getElementById(dId);
                        if (dEl) dEl.classList.add('related');
                        relatedBoxIds.push(dId);
                        container_fs_v.querySelectorAll('.svg-curve[data-from="'+f.id+'"][data-to="'+dId+'"]').forEach(function(curve) {
                            if (curve.dataset.type === 'f-d') curve.classList.add('highlight');
                        });
                    }
                });
                dimUnrelated(relatedBoxIds, '.svg-curve.highlight');
            });
            el.addEventListener('mouseleave', clearHighlights);
        });
        // Datasets
        datasets.forEach(function(d) {
            var el = document.getElementById(d.id);
            if (!el) return;
            el.addEventListener('mouseenter', function() {
                clearHighlights();
                el.classList.add('highlight');
                var relatedBoxIds = [d.id];
                // Related Features
                (datasetFeatureMap[d.id]||[]).forEach(function(fId) {
                    var fEl = document.getElementById(fId);
                    if (fEl) fEl.classList.add('related');
                    relatedBoxIds.push(fId);
                    container_fs_v.querySelectorAll('.svg-curve[data-from="'+fId+'"][data-to="'+d.id+'"]').forEach(function(curve) {
                        if (curve.dataset.type === 'f-d') curve.classList.add('highlight');
                    });
                });
                dimUnrelated(relatedBoxIds, '.svg-curve.highlight');
            });
            el.addEventListener('mouseleave', clearHighlights);
        });
    }
    drawMindMapLinks();

}
renderFeatureStoreMindMap(
    dataSources,
    featureProcesses,
    features,
    datasets,
    dataSourceMap,
    featureProcessMap,
    datasetFeatureMap
);
</script>
"""