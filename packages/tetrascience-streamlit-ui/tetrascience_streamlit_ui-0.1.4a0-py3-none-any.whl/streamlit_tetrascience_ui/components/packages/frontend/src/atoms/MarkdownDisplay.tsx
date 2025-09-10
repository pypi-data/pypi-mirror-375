import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { MarkdownDisplay, MarkdownDisplayProps } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StMarkdownDisplay({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    name,
    markdown = "# Default Markdown\nThis is default markdown content.",
    codeRenderer,
    className,
    ...markdownProps
  } = args as {
    name?: string
    markdown?: string
    codeRenderer?: MarkdownDisplayProps["codeRenderer"]
    className?: string
  } & Partial<MarkdownDisplayProps>

  // setFrameHeight should be called on first render and everytime the size might change (e.g. due to a DOM update).
  // Adding the theme here since it might effect the visual size of the component.
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  // Merge markdown display props
  const mergedMarkdownProps = {
    markdown,
    codeRenderer,
    ...markdownProps,
  }

  return (
    <div className={className}>
      <MarkdownDisplay {...mergedMarkdownProps} />
    </div>
  )
}

export default withStreamlitConnection(StMarkdownDisplay)
