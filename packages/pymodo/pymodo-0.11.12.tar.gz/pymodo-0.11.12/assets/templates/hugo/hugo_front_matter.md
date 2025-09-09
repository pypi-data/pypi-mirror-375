---
type: docs
title: {{.Name}}
{{if or (eq .Kind "struct") (eq .Kind "trait") -}}
weight: 100
{{- else if eq .Kind "function" -}}
weight: 200
{{- else if eq .Kind "module" -}}
weight: 300
{{- else if eq .Kind "package" -}}
weight: 400
{{- else  -}}
weight: 500
{{- end}}
---
