import {
  Streamlit,
  withStreamlitConnection,
  ComponentProps,
} from "streamlit-component-lib"
import React, { useEffect, ReactElement } from "react"
import { AppLayout, AppLayoutProps, LineGraph } from "tetrascience-ui"
import "tetrascience-ui/index.css"

/**
 * This is a React-based component template. The passed props are coming from the
 * Streamlit library. Your custom args can be accessed via the `args` props.
 */
function StAppLayout({
  args,
  disabled,
  theme,
}: ComponentProps<any>): ReactElement {
  const {
    userProfile = { name: "User" },
    hostname = "localhost",
    organization = { name: "Organization" },
    lineGraphConfig,
    ...appLayoutProps
  } = args as {
    userProfile?: {
      name: string
      avatar?: string
    }
    hostname?: string
    organization?: {
      name: string
      subtext?: string
      logo?: React.ReactNode
    }
    lineGraphConfig?: {
      data_series?: Array<{
        x: number[]
        y: number[]
        name: string
        color: string
        symbol?: string
      }>
      width?: number
      height?: number
      x_title?: string
      y_title?: string
      title?: string
      variant?: string
    }
  } & Partial<AppLayoutProps>

  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [theme])

  useEffect(() => {
    Streamlit.setComponentValue({
      event: "render",
      userProfile,
      hostname,
      organization,
    })
  }, [userProfile, hostname, organization])

  const mergedAppLayoutProps = {
    userProfile,
    hostname,
    organization,
    children: lineGraphConfig ? (
      <LineGraph
        dataSeries={
          lineGraphConfig.data_series?.map((series) => ({
            x: series.x || [],
            y: series.y || [],
            name: series.name || "",
            color: series.color || "#000000",
            symbol: series.symbol as any,
          })) || []
        }
        width={lineGraphConfig.width || 1000}
        height={lineGraphConfig.height || 600}
        xTitle={lineGraphConfig.x_title || "X Axis"}
        yTitle={lineGraphConfig.y_title || "Y Axis"}
        title={lineGraphConfig.title || "Line Graph"}
        variant={(lineGraphConfig.variant as any) || "lines"}
      />
    ) : undefined,
    ...appLayoutProps,
  }

  return <AppLayout {...mergedAppLayoutProps} />
}

export default withStreamlitConnection(StAppLayout)
