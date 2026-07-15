{{- define "sentinel-fusion-ai.name" -}}
sentinel-fusion-ai
{{- end -}}

{{- define "sentinel-fusion-ai.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "sentinel-fusion-ai.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "sentinel-fusion-ai.labels" -}}
app.kubernetes.io/name: {{ include "sentinel-fusion-ai.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: Helm
{{- end -}}
