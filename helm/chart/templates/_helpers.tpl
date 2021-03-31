{{/*
Expand the name of the chart.
*/}}
{{- define "visualizations.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name, accepts a dictionary
containing the key "dot" (value: . passed in from the root level)
and optionally, the key "region" (value: that deployment/service's region)
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "visualizations.fullname" -}}
{{ $regionName := (include "visualizations.regionName" .region) }}
{{- if .dot.Values.fullnameOverride }}
{{- printf "%s-%s" .dot.Values.fullnameOverride $regionName | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .dot.Chart.Name .dot.Values.nameOverride }}
{{- if contains $name .dot.Release.Name }}
{{- printf "%s-%s" .dot.Release.Name $regionName | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s-%s" .dot.Release.Name $name $regionName | trunc 63 | trimSuffix "-" }}
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
and optionally, the key "region" (value: that deployment/service's region)
*/}}
{{- define "visualizations.selectorLabels" -}}
app.kubernetes.io/name: {{ include "visualizations.name" .dot }}
{{- $regionName := (include "visualizations.regionName" .region) }}
app.kubernetes.io/instance: {{ printf "%s-%s" .dot.Release.Name $regionName | trimSuffix "-" }}
visualizations/release: {{ .dot.Release.Name }}
{{- end }}

{{/*
Returns region name, replacing slashes with hyphens. Expects the region name as input.
*/}}
{{- define "visualizations.regionName" -}}
{{- if . }}
{{- . | replace "/" "-" -}}
{{- end }}
{{- end }}

{{/*
Convert allowed origins to a comment-separated string
*/}}
{{- define "visualizations.allowedOrigins" -}}
{{- join "," .Values.allowedOrigins }}
{{- end }}
