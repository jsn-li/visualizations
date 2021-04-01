{{/*
Expand the name of the chart.
*/}}
{{- define "visualizations.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name, accepts a dictionary
containing the key "dot" (value: . passed in from the root level)
and optionally, the key "regionPath" (value: that deployment/service's region path)
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "visualizations.fullname" -}}
{{ $safeRegionName := (include "visualizations.safeRegionName" .regionPath) }}
{{- if .dot.Values.fullnameOverride }}
{{- printf "%s-%s" .dot.Values.fullnameOverride $safeRegionName | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .dot.Chart.Name .dot.Values.nameOverride }}
{{- if contains $name .dot.Release.Name }}
{{- printf "%s-%s" .dot.Release.Name $safeRegionName | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s-%s" .dot.Release.Name $name $safeRegionName | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "visualizations.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "visualizations.labels" -}}
helm.sh/chart: {{ include "visualizations.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels, accepts a dictionary containing the key "dot" (value: . passed in from the root level)
and optionally, the key "regionPath" (value: that deployment/service's region path)
*/}}
{{- define "visualizations.selectorLabels" -}}
app.kubernetes.io/name: {{ include "visualizations.name" .dot }}
{{- $safeRegionName := (include "visualizations.safeRegionName" .regionPath) }}
app.kubernetes.io/instance: {{ printf "%s-%s" .dot.Release.Name $safeRegionName | trimSuffix "-" }}
visualizations/release: {{ .dot.Release.Name }}
{{- end }}

{{/*
Returns a region name that is safe to append to resource names and selectors. Expects the region path as input.
*/}}
{{- define "visualizations.safeRegionName" -}}
{{- if . }}
{{- . | replace "/" "-" | lower -}}
{{- end }}
{{- end }}

{{/*
Convert allowed origins to a comment-separated string
*/}}
{{- define "visualizations.allowedOrigins" -}}
{{- join "," .Values.allowedOrigins }}
{{- end }}
