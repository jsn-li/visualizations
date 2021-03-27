{{/*
Expand the name of the chart.
*/}}
{{- define "visualizations.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "visualizations.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
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
Selector labels, accepts a dictionary contains the key "dot" (value: . passed in from the root level)
and optionally, the key "region" (value: that deployment/service's region)
*/}}
{{- define "visualizations.selectorLabels" -}}
app.kubernetes.io/name: {{ include "visualizations.name" .dot }}
{{- if .region }}
app.kubernetes.io/instance: {{ .dot.Release.Name }}-{{ .region }}
{{- else }}
app.kubernetes.io/instance: {{ .dot.Release.Name }}
{{- end }}
{{- end }}

{{/*
Convert allowed origins to a comment-separated string
*/}}
{{- define "visualizations.allowedOrigins" -}}
{{- join "," .Values.allowedOrigins }}
{{- end -}}
