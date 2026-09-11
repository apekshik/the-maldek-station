#include "StationOpeningWidget.h"
#include "Rendering/DrawElements.h"
#include "Styling/CoreStyle.h"
#include "Framework/Application/SlateApplication.h"
#include "Fonts/FontMeasure.h"
#include "Rendering/SlateRenderer.h"

int32 UStationOpeningWidget::NativePaint(const FPaintArgs& Args,const FGeometry& G,const FSlateRect& CullingRect,FSlateWindowElementList& Out,int32 Layer,const FWidgetStyle& Style,bool bParentEnabled) const
{
 Layer=Super::NativePaint(Args,G,CullingRect,Out,Layer,Style,bParentEnabled);
 const FVector2D Size=G.GetLocalSize();
 const auto Ramp=[](float T,float A,float B){return FMath::SmoothStep(A,B,T);};
 auto Text=[&](const FString& Value,float Y,int32 FontSize,FLinearColor Color)
 {
  const FSlateFontInfo Font=FCoreStyle::GetDefaultFontStyle("Regular",FontSize);
  const FVector2D Extent=FSlateApplication::Get().GetRenderer()->GetFontMeasureService()->Measure(Value,Font);
  FSlateDrawElement::MakeText(Out,++Layer,G.ToPaintGeometry(Extent,FSlateLayoutTransform(FVector2D((Size.X-Extent.X)*.5f,Y))),Value,Font,ESlateDrawEffect::None,Color);
 };
 const float Hint=Ramp(Elapsed,11.0f,13.0f)*(1-Ramp(Elapsed,HintEnd-1,HintEnd));
 if(Hint>0)
 {
  const float Top=Size.Y*.77f;
  const int32 FontSize=FMath::Clamp(FMath::RoundToInt(Size.X*.014f),12,20);
  Text(TEXT("F   Flashlight on / off"),Top+17,FontSize,bToggled?FLinearColor(.53f,.8f,.65f,Hint):FLinearColor(.9f,.93f,.92f,Hint));
  Text(TEXT("SCROLL   Up: tighter beam    Down: wider beam"),Top+53,FontSize,bFocused?FLinearColor(.53f,.8f,.65f,Hint):FLinearColor(.75f,.83f,.81f,Hint));
 }
 return Layer;
}
